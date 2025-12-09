import os
from ipaddress import IPv4Network, AddressValueError
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Ensure AWS credentials are available
if not (os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY')):
    print("AWS credentials are not set in the environment variables.")
    exit(1)

# Initialize a session using Amazon EC2
session = boto3.Session()
ec2_client = session.client('ec2')

# Function to fetch security group ID dynamically if not hardcoded
def get_security_group_id():
    # Implement logic to fetch security group ID based on criteria like tags or name
    response = ec2_client.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': ['default']}])
    if response['SecurityGroups']:
        return response['SecurityGroups'][0]['GroupId']
    else:
        raise ValueError("No default security group found.")

# Fetch SECURITY_GROUP_ID from environment variables or use a dynamic method
SECURITY_GROUP_ID = os.getenv('SECURITY_GROUP_ID', get_security_group_id())
if not SECURITY_GROUP_ID:
    print("Security Group ID is not set in the environment variables.")
    exit(1)

# Validate user input for PUBLIC_IP
def validate_ip():
    while True:
        PUBLIC_IP = input("Please enter a valid IPv4 address: ")
        try:
            IPv4Network(PUBLIC_IP)
            return PUBLIC_IP
        except AddressValueError:
            print("Invalid IP address. Please try again.")

# Function to add IP permissions to the security group
def add_ip_permission():
    ec2_client.authorize_security_group_ingress(
        GroupId=SECURITY_GROUP_ID,
        IpProtocol='tcp',
        FromPort=80,
        ToPort=80,
        CidrIp=PUBLIC_IP + '/32'
    )
    print(f"Added IP {PUBLIC_IP} to the security group.")

# Check and add IP permission if not already added
def check_ip_permission():
    response = ec2_client.describe_security_groups(GroupIds=[SECURITY_GROUP_ID])
    for ip_permission in response['SecurityGroups'][0]['IpPermissions']:
        if 'FromPort' in ip_permission and ip_permission['FromPort'] == 80 and 'IpProtocol' in ip_permission and ip_permission['IpProtocol'] == 'tcp':
            cidr_blocks = ip_permission.get('IpRanges', [])
            for block in cidr_blocks:
                if block['CidrIp'] == PUBLIC_IP + '/32':
                    print(f"IP {PUBLIC_IP} already has access.")
                    return
    add_ip_permission()

# Validate the PUBLIC_IP input before proceeding
PUBLIC_IP = validate_ip()
check_ip_permission()
