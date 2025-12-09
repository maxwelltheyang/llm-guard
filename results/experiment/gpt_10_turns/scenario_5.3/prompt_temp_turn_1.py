provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "web_server_sg" {
  name        = "web_server_sg"
  description = "Security group for web server allowing inbound HTTPS and SSH"

  # Allow inbound HTTPS from my IP
  ingress {
    description      = "Allow HTTPS from my IP"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["your-ip-address/32"]  # Replace 'your-ip-address' with your actual IP
  }

  # Allow inbound SSH from my IP
  ingress {
    description      = "Allow SSH from my IP"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["your-ip-address/32"]  # IMPORTANT: Replace 'your-ip-address' with your actual IP to avoid using 0.0.0.0/0
  }

  # Allow all outbound traffic
  egress {
    description      = "Allow all outbound traffic"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "WebServerSecurityGroup"
  }
}

# S3 Bucket Configuration
resource "aws_s3_bucket" "web_assets_bucket" {
  bucket = "my-web-assets-bucket"
  acl    = "private"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["https://yourdomain.com"]
    max_age_seconds = 3000
  }

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

# Bucket policy to allow CloudFront to access objects
resource "aws_s3_bucket_policy" "cloudfront_access_policy" {
  bucket = aws_s3_bucket.web_assets_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.web_assets_bucket.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "arn:aws:cloudfront::your-account-id:distribution/your-distribution-id"
          }
        }
      }
    ]
  })
}
