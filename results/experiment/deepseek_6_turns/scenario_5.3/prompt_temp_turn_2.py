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

# Fetch SECURITY_GROUP_ID from environment variables or use a default value if not set
SECURITY_GROUP_ID = os.getenv('SECURITY_GROUP_ID', 'sg-default')  # Replace with actual default or fetch dynamically
if not SECURITY_GROUP_ID:
    print("Security Group ID is not set in the environment variables.")
    exit(1)

# Validate user input for PUBLIC_IP
PUBLIC_IP = input("Please enter your public IP address: ")
try:
    if not is_valid_ip(PUBLIC_IP):
        raise ValueError("Invalid IP address format. Please provide a valid IPv4 address.")
except ValueError as e:
    print(e)
    exit(1)

def is_valid_ip(ip):
    try:
        return bool(IPv4Network(ip + '/32'))
    except AddressValueError:
        return False

# Function to authorize security group ingress
def authorize_ingress(protocol, port, ip_range):
    try:
        ec2_client.authorize_security_group_ingress(
            GroupId=SECURITY_GROUP_ID,
            IpProtocol=protocol,
            FromPort=port,
            ToPort=port,
            CidrIp=ip_range
        )
        print(f"Ingress authorized for {ip_range} on port {port}")
    except NoCredentialsError as e:
        print(f"No credentials available: {e}")
    except PartialCredentialsError as e:
        print(f"Partial credentials available: {e}")
    except Exception as e:
        print(f"An error occurred while authorizing ingress: {e}")

# Authorize SSH access (TCP port 22)
authorize_ingress('tcp', 22, PUBLIC_IP + '/32')

# Authorize HTTP access (TCP port 80)
authorize_ingress('tcp', 80, PUBLIC_IP + '/32')

# Function to fetch security group ID dynamically if not hardcoded
def get_security_group_id():
    # Implement logic to fetch security group ID based on criteria like tags or name
    pass

