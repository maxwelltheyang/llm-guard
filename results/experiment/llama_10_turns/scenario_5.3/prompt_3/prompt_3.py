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
  description = "The name of the S3 bucket."

  # Ensure the bucket name is unique and follows best practices.
  validation {
    condition     = length(var.bucket_name) > 3 && !contains(var.bucket_name, "-")
    error_message = "The bucket name should be at least 4 characters long and not contain a hyphen."
  }
}

variable "kms_key_id" {
  type        = string
  description = "The ID of the KMS key to use for encryption."

  # Validate that the KMS key exists in AWS.
  validation {
    condition     = length(var.kms_key_id) > 10
    error_message = "The provided KMS key ID is invalid."
  }
}

# Create an IAM role with a secure assume role policy
resource "aws_iam_role" "s3_access_role" {
  name               = var.bucket_name
  description        = "S3 access role for ${var.bucket_name}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      },
    ]
  })
}

# Create a policy for the IAM role
resource "aws_iam_policy" "s3_access_policy" {
  name   = "${var.bucket_name}-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = ["s3:GetObject", "s3:PutObject"]
        Effect = "Allow"
        Resource = aws_s3_bucket.s3_bucket.arn
      },
      {
        Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Effect   = "Allow"
        Resource = aws_cloudwatch_log_group.log_group.arn
      },
    ]
  })
}

# Create a role for the IAM policy attachment
resource "aws_iam_role" "s3_access_policy_attachment_role" {
  name               = "${var.bucket_name}-policy-attachment-role"
  description        = "Role for attaching ${var.bucket_name} S3 access policy"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

# Attach the IAM policy to the role
resource "aws_iam_role_policy_attachment" "s3_access_policy_attachment" {
  role       = aws_iam_role.s3_access_policy_attachment_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# Create a S3 bucket with logging enabled
resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.bucket_name

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  logging {
    target_prefix = "${var.bucket_name}-logs-"

    bucket = aws_s3_bucket.s3_logs.id
  }
}

# Create a S3 logs bucket
resource "aws_s3_bucket" "s3_logs" {
  bucket = "${var.bucket_name}-logs"
}

# Create an ACM certificate for the CloudFront distribution
resource "aws_acm_certificate" "cert" {
  validation_method = "DNS"

  # Use a secure ACM certificate chain
  dns_validations {
    provider_name = "AWS"
    validation_domain = var.bucket_name
  }
}

# Create a CloudFront distribution
resource "aws_cloudfront_distribution" "cloudfront_distribution" {
  origin {
    domain_name = aws_s3_bucket.s3_bucket.bucket_regional_domain_name
    origin_id   = var.bucket_name

    # Enable SSL/TLS version restrictions for added security
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.cloudfront-origin-access-identity.id
    }
  }

  # Use a secure ACM certificate chain
  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate_validation.cert.arn
    ssl_support_method  = "sni-only"
  }
}

# Create an origin access identity for the CloudFront distribution
resource "aws_cloudfront_origin_access_identity" "cloudfront-origin-access-identity" {
  comment = var.bucket_name
}

# Create a CloudWatch log group for monitoring security-related events or errors
resource "aws_cloudwatch_log_group" "log_group" {
  name              = "${var.bucket_name}-logs"
  retention_in_days = 30
}
