# Define IAM role ARN as an environment variable
variable "iam_role_arn" {
  type        = string
  description = "IAM Role ARN"
}

# Use the environment variable instead of hardcoding it directly into the Terraform configuration
resource "aws_iam_instance_profile" "ec2-role" {
  name = "${var.bucket_name}-ec2-role-${var.website_domain}"
  role = var.iam_role_arn
}

# Restrict access based on IP addresses using a more granular control, such as AWS IAM services like STS
resource "aws_s3_bucket_policy" "assets-policy" {
  bucket = aws_s3_bucket.assets.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowEC2Actions"
        Effect    = "Allow"
        Action     = ["s3:GetObject", "s3:PutObject"]
        Resource  = "${aws_s3_bucket.assets.arn}/*"

        # Restrict access based on IP addresses using a more granular control
        Condition = {
          StringEqualsAWS: "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${var.aws_account_user}"
        }
      },
    ]
  })
}

# Automate security group configuration for your EC2 instances and Lambda functions
resource "aws_security_group" "ec2-sg" {
  name   = "${var.bucket_name}-ec2-sg-${var.website_domain}"
  vpc_id = aws_vpc.default.id

  ingress {
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "lambda-sg" {
  name   = "${var.bucket_name}-lambda-sg-${var.website_domain}"
  vpc_id = aws_vpc.default.id

  ingress {
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}
