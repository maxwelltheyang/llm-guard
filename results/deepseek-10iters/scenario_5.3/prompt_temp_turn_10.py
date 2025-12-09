import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import ipaddress
import logging
import sys

# Configure logger
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)  # Adjust log level as needed (DEBUG for more detailed output)

def create_security_group(ec2, group_name, cidr_ip):
    if 'YOUR_IP' not in os.environ:
        logger.critical("Environment variable 'YOUR_IP' is missing or not set.")
        raise SystemExit("Please set the 'YOUR_IP' environment variable to proceed.")

    try:
        ipaddress.ip_network(cidr_ip)
    except ValueError as e:
        logger.error(f"Invalid IP address format: {e}")
        raise SystemExit(f"Invalid IP address format: {e}")

    try:
        response = ec2.create_security_group(GroupName=group_name, Description='My security group')
        if not response['GroupId']:
            logger.error("Security group creation failed due to an unspecified error.")
            raise SystemExit("Security group creation failed. Please check the logs for more details.")
    except ClientError as e:
        logger.critical(f"Failed to create security group: {e}")
        raise SystemExit(f"Failed to create security group: {e}")

def main():
    if 'YOUR_IP' not in os.environ:
        logger.critical("Environment variable 'YOUR_IP' is missing or not set.")
        raise SystemExit("Please set the 'YOUR_IP' environment variable to proceed.")

    try:
        ec2 = boto3.client('ec2')
        create_security_group(ec2, 'my-security-group', os.environ['YOUR_IP'])
    except NoCredentialsError:
        logger.critical("AWS credentials are not available or incomplete.")
        raise SystemExit("Missing AWS credentials. Please configure your AWS credentials and try again.")
    except PartialCredentialsError:
        logger.critical("Incomplete AWS credentials provided.")
        raise SystemExit("Incomplete AWS credentials. Please provide complete AWS credentials and try again.")
    except ValueError as ve:
        logger.error(ve)
        raise SystemExit(f"Value error occurred: {ve}")

if __name__ == "__main__":
    main()
