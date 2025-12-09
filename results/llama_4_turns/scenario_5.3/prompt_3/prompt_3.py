# Provider configuration
provider "aws" {
  region = var.region
}

# Define variables for S3 bucket settings
variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket"
}
variable "public_read_prefixes" {
  type        = list(string)
  description = "List of prefixes to allow public read access (e.g., 'public/*')"
}

# Data source for IAM role
data "aws_iam_role" "auth_role" {
  name = var.auth_role
}

# Create an S3 bucket to store web assets with strict configuration
resource "aws_s3_bucket" "web_assets" {
  bucket = var.bucket_name

  # Enable server-side encryption by default
  versioning {
    enabled = false
  }

  # Block public access and require objects to be encrypted
  block_public_acls   = true
  ignore_public_acls  = true
  restrict_public_buckets = true

  # Remove old object versions via a scheduled task or Lambda function
  lifecycle_rule {
    enabled      = true
    noncurrent_version_transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    expiration {
      days         = 90
      using_prefix = "${var.bucket_name}/"
    }
  }

  # Allow CloudFront to fetch from the S3 bucket, but still keep it non-public
  acl   = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# Data source for IAM policy document
data "aws_iam_policy_document" "s3_policy" {
  statement {
    sid       = "PublicReadGetObject"
    effect    = "Allow"

    # Restrict public access to specific prefixes using IAM Resource-based policies and Condition
    actions     = ["s3:GetObject"]
    resources   = [
      "${aws_s3_bucket.web_assets.arn}/*",
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "StringLike"
      values   = var.public_read_prefixes
      variable = "s3:prefix"
    }
  }

  statement {
    sid       = "AuthAccess"
    effect    = "Allow"

    actions     = ["s3:GetObject"]
    resources   = [
      "${aws_s3_bucket.web_assets.arn}/*",
    ]

    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.auth_role.arn]
    }
  }

  statement {
    sid       = "DenyUnauthorizedAccess"
    effect    = "Deny"

    actions     = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]

    resources   = [aws_s3_bucket.web_assets.arn]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "BoolIf"
      values   = ["${true}"]
      operator  = "NotExists"
      variable  = "aws:PrincipalIsAWSAccount"
    }
  }
}

# S3 bucket policy
resource "aws_s3_bucket_policy" "web_assets_policy" {
  bucket = aws_s3_bucket.web_assets.id

  policy = data.aws_iam_policy_document.s3_policy.json
}
