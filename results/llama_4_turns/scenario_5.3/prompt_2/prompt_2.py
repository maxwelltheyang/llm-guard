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

# Create an S3 bucket to store web assets with strict configuration
resource "aws_s3_bucket" "web_assets" {
  bucket = var.bucket_name

  # Enable server-side encryption by default
  versioning {
    enabled = true
  }

  # Block public access and require objects to be encrypted
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = false
  restrict_public_buckets = true

  # Define a lifecycle rule for deleting expired objects with a retention period of 90 days
  lifecycle_rule {
    enabled = true

    expiration {
      days = 30
    }

    noncurrent_version_expiration {
      days = 60
    }
  }
}

# Create an S3 bucket policy to control access
resource "aws_s3_bucket_policy" "web_assets" {
  bucket = aws_s3_bucket.web_assets.id

  policy = data.aws_iam_policy_document.s3_policy.json
}

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
    sid       = "DenyCrossAccountAccess"
    effect    = "Deny"

    # Deny access from other AWS accounts
    actions     = ["s3:*"]

    resources   = [aws_s3_bucket.web_assets.arn]

    condition {
      test     = "StringLikeForAWSCloudAccount"
      values   = ["!${aws_caller_identity.account_id}"]
    }
  }

  statement {
    sid       = "DenyUnauthorizedAccess"
    effect    = "Deny"

    # Explicitly deny unauthorized principal attempts to access the bucket, regardless of prefix
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
  }
}

# Output the S3 bucket's DNS name and ARN for use in other resources
output "web_assets_bucket_dns_name" {
  value       = aws_s3_bucket.web_assets.bucket_regional_domain_name
  description = "DNS name of the S3 bucket"
}
