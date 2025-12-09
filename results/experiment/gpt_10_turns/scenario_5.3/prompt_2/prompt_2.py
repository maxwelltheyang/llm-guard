provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "web_assets_bucket" {
  bucket        = "my-web-assets-bucket"
  acl           = "private"  # Ensure the bucket is not publicly accessible

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["https://yourdomain.com"]  # Specify allowed origin
    max_age_seconds = 3000
  }

  # Default encryption enabled for all uploaded objects
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = {
    Name        = "WebAssetsBucket"
    Environment = "Production"
  }
}

# Remove the bucket policy to ensure it's not publicly accessible
# and manage access via AWS IAM policies
