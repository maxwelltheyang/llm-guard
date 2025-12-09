import os
import boto3
import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Ensure all required environment variables are set
required_envs = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
missing_envs = [env for env in required_envs if os.getenv(env) is None]
if missing_envs:
    print(f"Error: The following environment variables are missing: {', '.join(missing_envs)}")
    exit(1)

# Validate and prompt for PUBLIC_IP
PUBLIC_IP = input("Please enter the public IP to authorize: ")
if not PUBLIC_IP or not is_valid_ip(PUBLIC_IP):
    print("Public IP is required and must be a valid IP address.")
    exit(1)

try:
    ec2_client = boto3.client('ec2')

    # Authorize SSH ingress with validated PUBLIC_IP
    ec2_client.authorize_security_group_ingress(
        GroupId=SECURITY_GROUP_ID,
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22,
        CidrIp=PUBLIC_IP
    )
    print("Successfully authorized SSH ingress for the provided public IP.")
except NoCredentialsError as e:
    print(f"AWS credentials are not available or incomplete: {e}")
    exit(1)
except PartialCredentialsError as e:
    print(f"Incomplete AWS credentials provided: {e}")
    exit(1)
except Exception as e:
    print(f"An error occurred while authorizing SSH ingress: {e}")
    exit(1)

try:
    # Authorize HTTPS ingress with validated PUBLIC_IP
    ec2_client.authorize_security_group_ingress(
        GroupId=SECURITY_GROUP_ID,
        IpProtocol='tcp',
        FromPort=443,
        ToPort=443,
        CidrIp=PUBLIC_IP
    )
    print("Successfully authorized HTTPS ingress for the provided public IP.")
except NoCredentialsError as e:
    print(f"AWS credentials are not available or incomplete: {e}")
    exit(1)
except PartialCredentialsError as e:
    print(f"Incomplete AWS credentials provided: {e}")
    exit(1)
except Exception as e:
    print(f"An error occurred while authorizing HTTPS ingress: {e}")
    exit(1)

def is_valid_ip(ip):
    from ipaddress import IPv4Network, AddressValueError
    try:
        return bool(IPv4Network(ip + '/32'))
    except AddressValueError:
        return False
