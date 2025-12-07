import boto3

def create_security_group():
    ec2 = boto3.client('ec2')

    response = ec2.create_security_group(
        GroupName='web-server-sg',
        Description='Security group for web server'
    )

    security_group_id = response['GroupId']

    # Allow inbound SSH (22) traffic from your IP
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22,
        CidrIp='your-ip/32'  # Replace with your actual IP address
    )

    # Allow inbound HTTPS (443) traffic from your IP
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpProtocol='tcp',
        FromPort=443,
        ToPort=443,
        CidrIp='your-ip/32'  # Replace with your actual IP address
    )

    return security_group_id

# Example usage:
# sg_id = create_security_group()
# print(f"Security Group ID: {sg_id}")
