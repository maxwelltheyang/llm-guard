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
  description = "Allowed SSH IP address"
}
# Restrict access to specific ports for HTTPS and SSH
variable "https_ports" {
  type        = list(number)
  description = "List of allowed HTTPS ports"
}
variable "ssh_port" {
  type        = number
  description = "Allowed SSH port"
}

# Create a security group for the web server that allows inbound HTTPS and SSH from trusted sources
resource "aws_security_group" "web_server_sg" {
  name        = "${var.environment}-web-server-sg"
  description = "Security Group for Web Server"
  vpc_id      = aws_vpc.web_server_vpc.id

  # Allow inbound HTTPS traffic on specified ports
  ingress {
    from_port   = var.https_ports[0]
    to_port     = var.https_ports[0]
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = var.https_ports[1]
    to_port     = var.https_ports[1]
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound SSH traffic on specified port
  ingress {
    from_port   = var.ssh_port
    to_port     = var.ssh_port
    protocol    = "tcp"
    cidr_blocks = [var.ssh_ip]
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
