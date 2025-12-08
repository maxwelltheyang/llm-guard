provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "web_assets" {
  bucket = "my-web-assets-bucket-unique"
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id = "expire_old_versions"

    noncurrent_version_expiration {
      days = 30
    }
  }

  tags = {
    Name        = "WebAssetsBucket"
    Environment = "Production"
  }
}

resource "aws_s3_bucket_policy" "web_assets_policy" {
  bucket = aws_s3_bucket.web_assets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.web_assets.arn}/*"
      }
    ]
  })
}
