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

# Create an S3 bucket to store web assets
resource "aws_s3_bucket" "web_assets" {
  bucket = var.bucket_name

  # Enable server-side encryption by default
  versioning {
    enabled = true
  }

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

    # Restrict public access to specific prefixes using IAM Resource-based policies
    actions     = ["s3:GetObject"]
    resources   = [
      "${aws_s3_bucket.web_assets.arn}/*",
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
  }

  statement {
    sid       = "DenyUnauthorizedAccess"
    effect    = "Deny"

    # Explicitly deny unauthorized principal attempts to access the bucket, regardless of prefix
    actions     = ["s3:*"]
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
