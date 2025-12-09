# Create a new security group
aws ec2 create-security-group --group-name WebServerSecurityGroup --description "Security group for web server"

# Get the ID of the newly created security group
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters Name=group-name,Values=WebServerSecurityGroup --query 'SecurityGroups[*].GroupId' --output text)

# Authorize inbound SSH traffic (port 22) from your IP
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 22 \
    --cidr <your-ip>/32

# Authorize inbound HTTPS traffic (port 443) from your IP
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 443 \
    --cidr <your-ip>/32
