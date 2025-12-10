# Import necessary providers and modules
provider "aws" {
  region = var.aws_region
}

# Define a secrets manager for storing sensitive data like AWS credentials
terraform {
  backend "s3" {}
}

# Configure the AWS provider
variable "aws_region" {
  type        = string
  description = "The AWS region to use."
}

# Input validation for variables using HCL2's built-in `validation` blocks
variable "bucket_name" {
  type        = string
  description = "The name of the S3 bucket to create."

  validation {
    condition     = length(var.bucket_name) > 0
    error_message = "Bucket name must be provided and cannot be empty."
  }
}

# Create an S3 bucket with a KMS key for encryption
resource "aws_s3_bucket" "example-bucket" {
  bucket = var.bucket_name

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }

  versioning {
    enabled = true
  }
}

# Create a KMS key for S3 encryption
resource "aws_kms_key" "example-key" {
  description             = "Example KMS Key"
  deletion_window_in_days = 10

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "Allow access for Key Admins"
        Effect    = "allow"
        Action    = ["kms:CreateGrant"]
        Resource  = aws_kms_key.example-key.arn
        Condition = {
          ArnEquals = {
            kms:GranteePrincipal = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
          }
        }
      },
      {
        Sid       = "Allow access for S3 Service Role"
        Effect    = "allow"
        Action    = ["kms:CreateKey", "kms:DescribeKey"]
        Resource  = aws_kms_key.example-key.arn
        Principal  = {
          Service = "s3.amazonaws.com"
        }
      },
      {
        Sid       = "Allow access for ELB Service Role"
        Effect    = "allow"
        Action    = ["kms:CreateGrant", "kms:GetKeyMetadata"]
        Resource  = aws_kms_key.example-key.arn
        Principal  = {
          Service = "elasticloadbalancing.amazonaws.com"
        }
      },
    ]
  })
}

# Create an S3 bucket policy to allow access from the KMS key
resource "aws_s3_bucket_policy" "example-policy" {
  bucket = aws_s3_bucket.example-bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "Allow access for S3 Service Role"
        Effect    = "allow"
        Action    = ["s3:GetObject", "s3:PutObject"]
        Resource  = aws_s3_bucket.example-bucket.arn
        Principal  = {
          Service = "s3.amazonaws.com"
        }
      },
    ]
  })
}

# Create an SSL/TLS certificate using AWS ACM
resource "aws_acm_certificate" "example-certificate" {
  domain_name       = var.bucket_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_route53_record.example-validation-record,
  ]
}

# Create a Route53 record set for the SSL/TLS certificate validation
resource "aws_route53_record" "example-validation-record" {
  zone_id         = var.route53_zone_id
  name            = aws_acm_certificate.example-certificate.domain_validation_options[0].resource_record_name
  records         = [aws_acm_certificate.example-certificate.domain_validation_options[0].resource_record_value]
  type            = aws_acm_certificate.example-certificate.domain_validation_options[0].resource_record_type
  ttl             = 60

  depends_on = [
    aws_acm_certificate.example-certificate,
  ]
}

# Configure the ELB listener rule to forward requests to the S3 bucket
resource "aws_lb_listener_rule" "example-listener-rule" {
  listener_arn = aws_lb_listener.example-lb.arn

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.example-target-group.arn
  }

  condition {
    field  = "path-pattern"
    values = ["/*"]
  }
}

# Create an ELB listener to handle HTTP requests
resource "aws_lb_listener" "example-lb" {
  load_balancer_arn = aws_lb.example-lb.arn

  protocol = "HTTPS"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.example-target-group.arn
  }
}

# Create an ELB target group to handle requests from the S3 bucket
resource "aws_lb_target_group" "example-target-group" {
  name     = var.bucket_name

  vpc_id = data.aws_vpc.current.id
}

# Create an ELB to handle HTTP requests
resource "aws_lb" "example-lb" {
  name               = var.bucket_name
  load_balancer_type = "application"

  subnets = data.aws_subnet_ids.default.ids
}
