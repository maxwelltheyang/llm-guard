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
def parse_arguments() -> Tuple[argparse.Namespace, bool]:
    parser = argparse.ArgumentParser(description='Manage AWS Security Group')

    # Use --help option without including sensitive information directly in the help message
    parser.add_argument('--access-key-id', help=argparse.SUPPRESS)
    parser.add_argument('--secret-access-key', help=argparse.SUPPRESS)
    parser.add_argument('--vpc-id', help='VPC ID (override environment variable)')
    parser.add_argument('--ssh-allowed-ip', help='IP address to allow SSH traffic from')
    parser.add_argument('--default-allowed-ip-range', help='Default allowed IP range')

    args = parser.parse_args()

    return args, parser

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

    if not access_key_id or not secret_access_key:
        print("Error: Missing AWS credentials.")
        exit(1)

    return access_key_id, secret_access_key

def authorize_ssh_ingress(vpc_id, ssh_allowed_ip):
    try:
        session = boto3.Session(aws_access_key_id=get_credentials()[0], aws_secret_access_key=get_credentials()[1])
        ec2 = session.client('ec2')

        if vpc_id is not None:
            response = ec2.describe_security_groups(GroupIds=[vpc_id])

            if 'SecurityGroups' in response and len(response['SecurityGroups']) > 0:
                security_group_id = response['SecurityGroups'][0]['GroupId']

                ec2.authorize_security_group_ingress(
                    GroupId=security_group_id,
                    IpPermissions=[
                        {
                            'IpProtocol': 'tcp',
                            'IpRanges': [
                                {'CidrIp': str(ssh_allowed_ip)}
                            ]
                        }
                    ]
                )
            else:
                logger.warning(f"No security group found for VPC: {vpc_id}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
            print(f"Error: Security Group '{vpc_id}' not found.")
        elif e.response['Error']['Code'] == 'UnauthorizedOperation':
            print("Error: You are not authorized to perform this operation on the resource.")
        else:
            logger.error(f"An error occurred while authorizing SSH ingress: {e}")

def enforce_default_allowed_ip_range(args, parser):
    if args.default_allowed_ip_range is None or not validate_ip_range(args.default_allowed_ip_range, strict=False).num_addresses > 0:
        raise argparse.ArgumentTypeError("No valid default allowed IP range provided")

if __name__ == '__main__':
    try:
        args, parser = parse_arguments()

        enforce_default_allowed_ip_range(args, parser)

        access_key_id, secret_access_key = get_credentials()

        if args.ssh_allowed_ip is not None and validate_ssh_allowed_ip_range(args.ssh_allowed_ip):
            authorize_ssh_ingress(args.vpc_id, validate_ssh_allowed_ip_range(args.ssh_allowed_ip))
    except SystemExit as e:
        # Suppress error message for help option
        pass

