import boto3
from botocore.exceptions import ClientError, NoCredentialsError, UnauthorizedOperation
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
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--vpc-id', help='VPC ID (override environment variable)')
    required_args.add_argument('--ssh-allowed-ip', help='IP address to allow SSH traffic from')

    args = parser.parse_args()

    if hasattr(args, 'access_key') and not args.vpc_id:
        parser.error("Error: Access key provided without VPC ID")

    return args, parser

def validate_ip_range(ip_range: str) -> ipaddress.IPv4Network:
    try:
        return ipaddress.ip_network(ip_range)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid IP range provided: {e}")

def enforce_default_allowed_ip_range(args, parser):
    if args.default_allowed_ip_range is not None:
        try:
            validate_ip_range(args.default_allowed_ip_range)
        except argparse.ArgumentTypeError as e:
            raise argparse.ArgumentError(parser.error(f"No valid default allowed IP range provided: {e}"))

if __name__ == '__main__':
    try:
        args, parser = parse_arguments()

        enforce_default_allowed_ip_range(args, parser)

        if 'AWS_ACCESS_KEY_ID' not in os.environ or 'AWS_SECRET_ACCESS_KEY' not in os.environ:
            raise ValueError("Error: AWS credentials environment variables are missing")

        access_key_id, secret_access_key = os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY']

        if args.ssh_allowed_ip is not None and validate_ip_range(args.ssh_allowed_ip):
            try:
                authorize_ssh_ingress(args.vpc_id, validate_ip_range(args.ssh_allowed_ip))
            except ClientError as e:
                if isinstance(e.response['Error']['Code'], UnauthorizedOperation):
                    print(f"Unauthorized operation: {e}")
                else:
                    raise e
    except SystemExit as e:
        # Suppress error message for help option
        pass

def get_credentials() -> (str, str):
    try:
        access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

        if len(access_key_id) < 10 or len(secret_access_key) < 20:
            raise ValueError("Error: AWS credentials environment variables are compromised")

        return access_key_id, secret_access_key
    except KeyError as e:
        print(f"Error: Environment variable {e} not found. Please set it properly.")

def authorize_ssh_ingress(vpc_id: str, ip_range: ipaddress.IPv4Network):
    session = boto3.Session(aws_access_key_id=get_credentials()[0], aws_secret_access_key=get_credentials()[1])
    ec2_client = session.client('ec2')

    if vpc_id is not None:
        response = ec2_client.describe_security_groups(GroupIds=[vpc_id])

        if 'SecurityGroups' in response and len(response['SecurityGroups']) > 0:
            security_group_id = response['SecurityGroups'][0]['GroupId']

            ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'IpRanges': [
                            {'CidrIp': str(ip_range)}
                        ]
                    }
                ]
            )
        else:
            print(f"No security group found for VPC: {vpc_id}")

def main():
    try:
        # Rest of your code here
        pass
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    main()
