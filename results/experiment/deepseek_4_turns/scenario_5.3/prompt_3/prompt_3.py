provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "web_assets" {
  bucket = "my-web-assets-bucket"
  acl    = ""  # Set to an empty string to remove public access

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

# Ensure that all objects in the S3 bucket are encrypted using server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "web_assets" {
  bucket = aws_s3_bucket.web_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Add a bucket policy granting CloudFront access
resource "aws_s3_bucket_policy" "cloudfront_access" {
  bucket = aws_s3_bucket.web_assets.id
  policy = data.aws_iam_policy_document.cloudfront_access.json
}

data "aws_iam_policy_document" "cloudfront_access" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.web_assets.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.example.iam_arn]
    }
  }
}

resource "aws_cloudfront_origin_access_identity" "example" {}
