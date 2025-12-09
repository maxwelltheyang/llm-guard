import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import ipaddress
import logging
import sys

# Configure local logging for better control over log levels and outputs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_security_group(ec2, group_name, cidr_ip):
    if not os.getenv('YOUR_IP'):
        logger.critical("Please set the YOUR_IP environment variable to proceed.")
        raise ValueError("Missing required environment variable: YOUR_IP")

    try:
        ipaddress.ip_network(cidr_ip)
    except ValueError as e:
        logger.error(f"Invalid IP address or CIDR notation: {e}")
        raise ValueError("Invalid IP address or CIDR notation")

    try:
        response = ec2.create_security_group(GroupName=group_name, Description='My security group', VpcId='vpc-12345678')
        if not response:
            logger.error("Security group creation failed due to an unspecified error.")
            raise ValueError("Security group creation failed")
    except ClientError as e:
        logger.critical(f"Failed to create security group: {e}")
        raise ValueError("Failed to create security group")

def main():
    if not os.getenv('YOUR_IP'):
        logger.critical("Please set the YOUR_IP environment variable to proceed.")
        raise ValueError("Missing required environment variable: YOUR_IP")

    try:
        ec2 = boto3.client('ec2')
        create_security_group(ec2, 'my-security-group', os.getenv('YOUR_IP'))
    except NoCredentialsError:
        logger.critical("AWS credentials are not available or incomplete.")
        raise SystemExit("Missing AWS credentials")
    except PartialCredentialsError:
        logger.critical("Incomplete AWS credentials provided.")
        raise SystemExit("Incomplete AWS credentials")
    except ValueError as ve:
        logger.error(ve)
        sys.exit(1)

if __name__ == "__main__":
    main()
