provider "aws" {
  region = "us-west-2" # Change this to your desired region
}

# Variable to hold the IP address that should be allowed access
variable "allowed_ip" {
  description = "The IP address to allow SSH and HTTPS access from."
  type        = string

  validation {
    condition     = can(regex("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$", var.allowed_ip))
    error_message = "The allowed IP address must be a valid IPv4 address."
  }
}

# Security Group for web server allowing SSH (port 22) and HTTPS (port 443) traffic
resource "aws_security_group" "web_server_sg" {
  name_prefix = "web_server_sg_"
  description = "Security Group for web server allowing SSH (port 22) and HTTPS (port 443) traffic from the specified IP address."

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web_server_sg"
  }
}
