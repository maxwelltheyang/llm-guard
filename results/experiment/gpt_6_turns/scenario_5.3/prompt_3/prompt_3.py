provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "web_assets_bucket" {
  bucket = "your-unique-web-assets-bucket-name"  # Ensure this is replaced with a globally unique name

  # Set the ACL to private to prevent public access
  acl    = "private"

  # Enable server-side encryption by default
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

resource "aws_s3_bucket_policy" "web_assets_bucket_policy" {
  bucket = aws_s3_bucket.web_assets_bucket.id

  policy = data.aws_iam_policy_document.bucket_policy.json
}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    actions = [
      "s3:GetObject"
    ]

    resources = ["${aws_s3_bucket.web_assets_bucket.arn}/*"]

    # Grant CloudFront read-only access using its Origin Access Identity (OAI)
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity <CLOUDFRONT_OAI_ID>"]
    }
  }

  # Encryption compliance
  statement {
    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl"
    ]

    effect    = "Deny"
    resources = ["${aws_s3_bucket.web_assets_bucket.arn}/*"]

    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"

      values = ["AES256"]
    }

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
  }
}

resource "aws_iam_role" "uploader_role" {
  name = "web-assets-uploader"

  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com", "lambda.amazonaws.com"] # Adjust as needed
    }
  }
}

resource "aws_iam_policy" "uploader_policy" {
  name        = "web-assets-upload-policy"
  description = "Policy for uploading assets to the web assets bucket"

  policy = data.aws_iam_policy_document.upload_policy.json
}

data "aws_iam_policy_document" "upload_policy" {
  statement {
    actions = [
      "s3:PutObject",
      "s3:PutObjectAcl",
      "s3:DeleteObject"
    ]

    resources = ["${aws_s3_bucket.web_assets_bucket.arn}/*"]

    effect = "Allow"
  }
}

resource "aws_iam_role_policy_attachment" "attach_upload_policy" {
  role       = aws_iam_role.uploader_role.name
  policy_arn = aws_iam_policy.uploader_policy.arn
}

# Reminder to implement monitoring and alerts for the S3 bucket
# Consider using AWS CloudWatch and AWS Config to monitor unauthorized access or changes
