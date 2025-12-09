provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "example" {
  bucket = "example-bucket"
}

# Explicit Deny for All Others
resource "aws_s3_bucket_policy" "example" {
  bucket = aws_s3_bucket.example.id

  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [
      {
        Sid: "AllowPublicRead",
        Effect: "Allow",
        Principal: "*",
        Action: ["s3:GetObject"],
        Resource: "${aws_s3_bucket.example.arn}/*"
      },
      {
        Effect: "Deny",
        Principal: "*",
        Action: ["s3:*"],
        Resource: "${aws_s3_bucket.example.arn}/*"
      }
    ]
  })
}

# Avoid Public Access by Default
resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Least Privilege Principle for IAM Role
resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version: "2012-10-17",
    Statement: [
      {
        Action: "sts:AssumeRole",
        Principal: {
          Service: "lambda.amazonaws.com"
        },
        Effect: "Allow"
      }
    ]
  })
}

# Specific Policy for Lambda Execution Role
resource "aws_iam_role_policy" "example" {
  name = "example-policy"
  role = aws_iam_role.example.id

  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [
      {
        Action: ["s3:GetObject"],
        Effect: "Allow",
        Resource: "${aws_s3_bucket.example.arn}/*"
      }
    ]
  })
}
