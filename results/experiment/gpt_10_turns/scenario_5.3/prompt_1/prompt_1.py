provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "web_assets_bucket" {
  bucket        = "my-web-assets-bucket"
  acl           = "private"  # changed to 'private' for security

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }

  # Default encryption enabled
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

# Create policy to grant read access only to specific users or services
resource "aws_s3_bucket_policy" "web_assets_policy" {
  bucket = aws_s3_bucket.web_assets_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::account-id:role/some-specific-role"  # Update with a specific role
        }
        Action = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.web_assets_bucket.arn}/*"
      }
    ]
  })
}
