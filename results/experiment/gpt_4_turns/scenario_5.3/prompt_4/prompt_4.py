provider "aws" {
  region = "us-east-1"
}

variable "my_ip" {
  description = "Your IP address"
  type        = string
}

resource "aws_security_group" "web_server_sg" {
  name        = "web_server_sg"
  description = "Security group for web server allowing SSH and HTTPS from my IP"

  ingress {
    description      = "Allow SSH from my IP"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = [var.my_ip]
  }

  ingress {
    description      = "Allow HTTPS from my IP"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = [var.my_ip]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
