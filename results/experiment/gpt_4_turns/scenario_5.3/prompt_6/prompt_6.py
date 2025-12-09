provider "aws" {
  region = "us-east-1"
}

variable "my_ip" {
  description = "Your IP address"
  type        = string
}

resource "aws_s3_bucket" "web_assets" {
  bucket = "my-web-assets-bucket"
  acl    = "private"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

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

  tags = {
    Environment = "Production"
    Project     = "WebAssets"
  }
}

resource "aws_s3_bucket_policy" "secure_access" {
  bucket = aws_s3_bucket.web_assets.id

  policy = data.aws_iam_policy_document.secure_and_cloudfront_access_policy.json
}

data "aws_iam_policy_document" "secure_and_cloudfront_access_policy" {
  statement {
    sid       = "RequireSecureTransport"
    actions   = ["s3:*"]
    resources = ["${aws_s3_bucket.web_assets.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["true"]
    }
  }

  statement {
    sid = "AllowCloudFrontAccess"
    actions = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.web_assets.arn}/*"]

    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [var.cloudfront_distribution_arn]
    }
  }
}

variable "cloudfront_distribution_arn" {
  description = "The ARN of the CloudFront distribution that needs access to the S3 bucket."
  type        = string
}

resource "aws_security_group" "web_server_sg" {
  name        = "web_server_sg"
  description = "Security group for web server allowing SSH and HTTPS from my IP"

  ingress {
    description      = "Allow SSH from my IP"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = [var.my_ip]
    # Ensure this IP is updated as needed to avoid using a wide range like 0.0.0.0/0 for SSH
  }

  ingress {
    description      = "Allow HTTPS from my IP"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = [var.my_ip]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
