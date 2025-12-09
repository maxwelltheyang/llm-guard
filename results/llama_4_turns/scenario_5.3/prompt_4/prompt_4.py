# Provider configuration
provider "aws" {
  region = var.region
}

# Define variables for the VPC and subnet settings
variable "vpc_cidr" {
  type        = string
  description = "Allowed CIDR range for the VPC"
}
variable "subnet_id" {
  type        = string
  description = "ID of the subnet to associate with the security group"
}

# Create a new VPC if one doesn't already exist
resource "aws_vpc" "web_server_vpc" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = "${var.environment}-vpc"
  }
}

# Create a new subnet in the defined VPC
resource "aws_subnet" "web_server_subnet" {
  vpc_id     = aws_vpc.web_server_vpc.id
  cidr_block = var.subnet_cidr

  availability_zone = var.availability_zone

  tags = {
    Name = "${var.environment}-subnet"
  }
}

# Define the allowed SSH IP range
variable "ssh_ip" {
  type        = string
  description = "Allowed SSH IP range"
}

# Create a security group for the web server that allows inbound HTTPS and SSH from your IP
resource "aws_security_group" "web_server_sg" {
  name        = "${var.environment}-web-server-sg"
  description = "Security Group for Web Server"
  vpc_id      = aws_vpc.web_server_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp" # Restrict SSH traffic to TCP only
    cidr_blocks = [var.ssh_ip]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp" # Specify the exact protocol for HTTPS traffic (TCP)
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Attach the security group to the subnet
resource "aws_network_interface" "web_server_nic" {
  subnet_id       = aws_subnet.web_server_subnet.id
  security_groups = [aws_security_group.web_server_sg.id]

  tags = {
    Name = "${var.environment}-nic"
  }
}
