provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "web_assets_bucket" {
  bucket = "your-unique-web-assets-bucket-name"  # Ensure this is replaced with a globally unique name
  acl    = "public-read"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags = {
    Name        = "WebAssetsBucket"
    Environment = "Production"
  }
}

resource "aws_s3_bucket_policy" "web_assets_bucket_policy" {
  bucket = aws_s3_bucket.web_assets_bucket.id

  policy = data.aws_iam_policy_document.public_read_policy.json
}

data "aws_iam_policy_document" "public_read_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.web_assets_bucket.arn}/*"]

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
