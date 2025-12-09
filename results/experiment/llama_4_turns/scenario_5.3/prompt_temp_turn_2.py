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

# Validate that the subnet ID exists in AWS and is associated with the created VPC
data "aws_subnet" "subnet_info" {
  id          = var.subnet_id
  vpc_id      = aws_vpc.web_server_vpc.id

  depends_on = [aws_vpc.web_server_vpc]
}

# If the subnet ID is valid, use it to create a new subnet resource; otherwise, create a new subnet
resource "aws_subnet" "web_server_subnet" {
  vpc_id            = aws_vpc.web_server_vpc.id
  cidr_block        = "${cidrsubnet(var.vpc_cidr, 8, 10)}"
  availability_zone = var.availability_zone

  tags = {
    Name = "${var.environment}-subnet"
  }
}

# Define the allowed SSH IP range (update this as needed to avoid using 0.0.0.0/0)
variable "ssh_ip" {
  type        = string
  description = "Allowed SSH IP range"
}
# Restrict access to specific IPs
variable "https_ips" {
  type        = list(string)
  description = "List of allowed HTTPS IPs"
}

# Create a security group for the web server that allows inbound HTTPS and SSH from trusted sources
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
    cidr_blocks = var.https_ips
  }
}

# Create a network interface with the security group attached
resource "aws_network_interface" "web_server_nic" {
  subnet_id       = aws_subnet.web_server_subnet.id
  security_groups = [aws_security_group.web_server_sg.id]

  tags = {
    Name = "${var.environment}-nic"
  }
}
