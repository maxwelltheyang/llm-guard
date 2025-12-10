# Import the AWS SDK library for Python
import boto3
from botocore.exceptions import ClientError
import os
import logging
import mimetypes
import getpass
import hashlib
import re
import argparse

# Set up argument parsing to allow command-line override of credentials and VPC ID
parser = argparse.ArgumentParser(description='Manage AWS Security Group')
parser.add_argument('--access-key-id', help='AWS Access Key ID (override environment variable)')
parser.add_argument('--secret-access-key', help='AWS Secret Access Key (override environment variable)')
parser.add_argument('--vpc-id', help='VPC ID (override environment variable)')

# Set up logging with a higher level (ERROR) to prevent capturing sensitive information
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Load environment variables for credentials and IP address, overriding from command-line arguments if provided
args = parser.parse_args()
aws_access_key_id = args.access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
vpc_id = args.vpc_id or os.environ.get('VPC_ID')

# Validate vpc_id format
if not re.match(r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$', vpc_id):
    logger.error("Invalid VPC ID format. Please use a valid UUID.")
    raise ValueError("Invalid VPC ID format")

# Create an EC2 client object to interact with EC2 resources
ec2 = boto3.client('ec2')

def create_security_group(vpc_id):
    try:
        response = ec2.create_security_group(
            Description='Web Server Security Group',
            GroupName='web-server-sg',
            VpcId=vpc_id
        )
        logger.info(f"Security group created: {response['GroupId']}")
        return response['GroupId']
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidVpc.VpcNotFound':
            logger.error("The specified VPC does not exist")
        elif e.response['Error']['Code'] == 'DryRunOperation':
            logger.info("No changes to make.")
        else:
            logger.error(f"Failed to create security group: {e}")

def authorize_security_group_ingress(security_group_id):
    try:
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 443,
                 'ToPort': 443,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ]
        )
    except ClientError as e:
        logger.error(f"Failed to authorize security group ingress: {e}")

def get_secret_access_key():
    # Prompt for secret access key securely using getpass
    return getpass.getpass("Enter your AWS Secret Access Key: ")

# Use argument parsing and environment variables for authentication instead of hardcoding credentials
if not aws_access_key_id:
    logger.error("AWS Access Key ID is required")
    raise ValueError("AWS Access Key ID is required")

if args.secret_access_key or 'AWS_SECRET_ACCESS_KEY' in os.environ:
    # If secret access key is provided through command-line argument or environment variable, use it
    aws_secret_access_key = args.secret_access_key or os.environ['AWS_SECRET_ACCESS_KEY']
else:
    # Otherwise, prompt user for secret access key securely using getpass
    aws_secret_access_key = get_secret_access_key()

ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

security_group_id = create_security_group(vpc_id)
authorize_security_group_ingress(security_group_id)

print(f"Security group created and configured in region: {ec2.meta.region_name}")
