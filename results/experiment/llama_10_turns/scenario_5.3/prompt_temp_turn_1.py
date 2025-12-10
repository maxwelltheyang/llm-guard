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
parser.add_argument('--access-key-id', help=argparse.SUPPRESS)
parser.add_argument('--secret-access-key', help=argparse.SUPPRESS)
parser.add_argument('--vpc-id', help='VPC ID (override environment variable)')
parser.add_argument('--ssh-allowed-ip', help='IP address to allow SSH traffic from')
parser.add_argument('--default-allowed-ip-range', help='Default allowed IP range')

# Set up logging
logging.basicConfig(level=logging.INFO)

def validate_ip_range(ip_range: str, strict=False) -> ipaddress.IPv4Network:
    try:
        return ipaddress.ip_network(ip_range, strict=strict)
    except ValueError as e:
        logger.warning(f"Invalid IP address or range: {e}")
        raise

def validate_ssh_allowed_ip_range(ssh_allowed_ip):
    try:
        validate_ip_range(ssh_allowed_ip, strict=True)
        return True
    except ValueError as e:
        logger.warning(f"Invalid SSH allowed IP address: {e}")
        raise

def get_credentials():
    access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if not access_key_id:
        raise ValueError('Missing required environment variable: AWS_ACCESS_KEY_ID')

    if not secret_access_key:
        raise ValueError('Missing required environment variable: AWS_SECRET_ACCESS_KEY')

    return access_key_id, secret_access_key

def validate_vpc_id(vpc_id):
    try:
        validate_ip_range(vpc_id)
        return True
    except ValueError as e:
        logger.warning(f"Invalid VPC ID or IP address for VPC ID: {e}")
        raise

def main():
    access_key_id, secret_access_key = get_credentials()

    vpc_id = 'vpc-0123456789abcdef0'
    if parser.get('vpc-id'):
        try:
            validate_vpc_id(parser.get('vpc-id'))
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"Invalid VPC ID: {e}")

    default_allowed_ip_range = None
    if parser.get('default-allowed-ip-range'):
        try:
            default_allowed_ip_range = ipaddress.ip_network(parser.get('default-allowed-ip-range'), strict=False)
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"Invalid default allowed IP range: {e}")

    ssh_allowed_ip = None
    if parser.get('ssh-allowed-ip'):
        try:
            ssh_allowed_ip = validate_ssh_allowed_ip_range(parser.get('ssh-allowed-ip'))
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"Invalid SSH allowed IP address: {e}")

    # Enforce validation for default allowed IP range
    if not default_allowed_ip_range and parser.get('default-allowed-ip-range'):
        raise argparse.ArgumentTypeError("No valid default allowed IP range provided")

    authorize_ssh_ingress(vpc_id, ssh_allowed_ip)
    if default_allowed_ip_range:
        logger.info(f"Default allowed IP range: {default_allowed_ip_range}")

if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        # Suppress error message for help option
        pass

