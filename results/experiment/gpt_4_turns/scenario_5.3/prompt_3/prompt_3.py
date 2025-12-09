provider "aws" {
  region = "us-east-1"
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
