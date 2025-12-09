# Define variables
variable "bucket_name" {
  type        = string
}

variable "acl" {
  type        = string
  default     = "public-read"
}

variable "versioning_enabled" {
  type        = bool
  default     = false
}

variable "website_domain" {
  type        = string
}

# Define the S3 bucket resource
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name

  acl   = var.acl
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource = "${aws_s3_bucket.this.arn}/*"
      }
    ]
  })

  versioning {
    enabled = var.versioning_enabled
  }

  website {
    index_document = "index.html"

    routing_rule {
      redirect_type = " permanant"
      hostname      = "*.${var.website_domain}"
      status_code   = "301"

      replacement_key                  = "${aws_s3_bucket.this.id}.s3.${var.website_domain}"
      replacement_path                = "/${aws_s3_bucket.this.id}/"
    }
  }

}

# Output the bucket URL
output "bucket_url" {
  value       = "https://${aws_s3_bucket.this.website_endpoint}${var.bucket_name}"
}
