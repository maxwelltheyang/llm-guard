import boto3

def create_security_group():
    ec2 = boto3.client('ec2')
    my_ip = "YOUR_IP_ADDRESS"  # Replace with your actual IP address

    # Create a security group
    response = ec2.create_security_group(
        GroupName='WebServerSG',
        Description='Security group for web server with inbound HTTPS and SSH'
    )
    security_group_id = response['GroupId']

    # Authorize inbound rules
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': f'{my_ip}/32'}],
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': f'{my_ip}/32'}],
            }
        ]
    )

    return security_group_id

create_security_group()
