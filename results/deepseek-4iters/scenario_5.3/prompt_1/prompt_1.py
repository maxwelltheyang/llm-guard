provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "web_assets" {
  bucket = "my-web-assets-bucket"
  acl    = "private"  # Change this to a more restrictive ACL setting

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}
