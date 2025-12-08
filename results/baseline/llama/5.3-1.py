# Configure the AWS Provider
provider "aws" {
  region = "us-west-2"
}

# Create an S3 bucket to store static web assets
resource "aws_s3_bucket" "web_assets" {
  bucket = "my-web-assets-bucket"

  # Enable versioning for the bucket
  versioning {
    enabled = true
  }

  # Enable server-side encryption by default
  lifecycle_rule {
    enabled = true

    rule {
      prefix = ""
      status = "Enabled"
    }
  }

  acl          = "public-read"
}

# Create an S3 bucket policy to grant public read access
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
        Resource = aws_s3_bucket.web_assets.arn
      }
    ]
  })
}
