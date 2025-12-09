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
    # Check if the IP permission already exists
    response = ec2_client.describe_security_group_rules(Filters=[{'Name': 'ip-permission.cidr', 'Values': [validate_ip()]}, {'Name': 'ip-permission.from-port', 'Values': [80]}, {'Name': 'ip-permission.to-port', 'Values': [80]}])
    if not response['SecurityGroupRules']:
        ec2_client.authorize_security_group_ingress(
            GroupId=SECURITY_GROUP_ID,
            IpProtocol='tcp',
            FromPort=80,
            ToPort=80,
            CidrIp=validate_ip()
        )
        print(f"Added IP permission for {validate_ip()} to security group.")
    else:
        print(f"IP permission for {validate_ip()} already exists in the security group.")

# Main function to run the script
def main():
    PUBLIC_IP = validate_ip()
    add_ip_permission()

if __name__ == "__main__":
    main()
