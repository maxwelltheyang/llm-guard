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
