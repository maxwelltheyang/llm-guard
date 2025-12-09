#!/usr/bin/env bash

# Retrieve current public IP address
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/)

# Create a new security group with environmental variables for name and description
SECURITY_GROUP_NAME="WebServerSecurityGroup"
SECURITY_GROUP_DESCRIPTION="Security group for web server allowing SSH (22) and HTTPS (443)"
aws ec2 create-security-group --group-name $SECURITY_GROUP_NAME --description "$SECURITY_GROUP_DESCRIPTION"

# Get the ID of the newly created security group
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters Name=group-name,Values=$SECURITY_GROUP_NAME --query 'SecurityGroups[*].GroupId' --output text)

# Authorize inbound SSH traffic (port 22) from the retrieved IP
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr $PUBLIC_IP/32

# Authorize inbound HTTPS traffic (port 443) from the retrieved IP
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 443 \
    --cidr $PUBLIC_IP/32
