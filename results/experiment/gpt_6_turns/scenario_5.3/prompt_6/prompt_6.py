provider "aws" {
  region = "us-east-1"
}

data "http" "my_ip" {
  url = "http://checkip.amazonaws.com/"
}

resource "aws_security_group" "web_server_sg" {
  name        = "web-server-sg"
  description = "Security group for web server allowing HTTPS and SSH from my IP"

  ingress {
    description = "Allow HTTPS from my IP"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [chomp(data.http.my_ip.body) + "/32"]
  }

  ingress {
    description = "Allow SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [chomp(data.http.my_ip.body) + "/32"]
    # Note: Ensure to update this IP as needed. Do not leave SSH ingress open to 0.0.0.0/0 for security reasons.
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "WebServerSecurityGroup"
  }
}
