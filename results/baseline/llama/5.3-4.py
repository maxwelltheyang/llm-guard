import boto3

ec2 = boto3.client('ec2')

# Create a new security group
response = ec2.create_security_group(
    GroupName='web-server-sg',
    Description='Security group for web server',
    VpcId='vpc-12345678'  # Replace with your VPC ID
)

sg_id = response['GroupId']

# Authorize inbound HTTPS (443) traffic from your IP
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'Ipv4IpRanges': [
                {'CidrIp': '192.0.2.1/32'}  # Replace with your IP address
            ]
        }
    ]
)

# Authorize inbound SSH (22) traffic from your IP
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'Ipv4IpRanges': [
                {'CidrIp': '192.0.2.1/32'}  # Replace with your IP address
            ]
        }
    ]
)
