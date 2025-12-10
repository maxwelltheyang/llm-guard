import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
import logging
import mimetypes
import argparse
import ipaddress
import getpass
import boto3
from botocore.exceptions import NoCredentialsError
import json
from typing import Tuple, List

# Set up argument parsing to allow command-line override of credentials and VPC ID
parser = argparse.ArgumentParser(description='Manage AWS Security Group')
parser.add_argument('--access-key-id', help='AWS Access Key ID (override environment variable)')
parser.add_argument('--secret-access-key', help='AWS Secret Access Key (override environment variable)')
parser.add_argument('--vpc-id', help='VPC ID (override environment variable)')
parser.add_argument('--ssh-allowed-ip', help='IP address to allow SSH traffic from')
parser.add_argument('--default-allowed-ip-range', help='Default allowed IP range')

# Set up logging
logging.basicConfig(level=logging.INFO)

def validate_ssh_allowed_ip_range(ssh_allowed_ip):
    try:
        ipaddress.ip_network(ssh_allowed_ip, strict=False)
        return True
    except ValueError as e:
        logger.warning(f"Invalid SSH allowed IP address: {e}")
        raise

def main():
    access_key_id, secret_access_key = get_credentials()

    vpc_id = 'vpc-0123456789abcdef0'

    if parser.get('ssh-allowed-ip'):
        ssh_allowed_ip = validate_ssh_allowed_ip_range(parser.get('ssh-allowed-ip'))
        authorize_ssh_ingress(vpc_id, ssh_allowed_ip)
    else:
        logger.warning("SSH allowed IP address not provided; skipping SSH ingress rule.")

    if parser.get('default-allowed-ip-range'):
        default_allowed_ip_range = parser.get('default-allowed-ip-range')
        logger.info(f"Default allowed IP range: {default_allowed_ip_range}")
    else:
        default_allowed_ip_range = '192.168.1.0/24'
        logger.warning("No default allowed IP range provided; using default value.")

def get_credentials():
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if not access_key_id:
        raise ValueError('Missing required environment variable: AWS_ACCESS_KEY_ID')

    if not secret_access_key:
        raise ValueError('Missing required environment variable: AWS_SECRET_ACCESS_KEY')

    return access_key_id, secret_access_key

if __name__ == "__main__":
    main()
