import os
import boto3
import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Ensure required environment variables are set
required_envs = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
missing_envs = [env for env in required_envs if os.getenv(env) is None]
if missing_envs:
    print(f"The following environment variables are missing: {', '.join(missing_envs)}")
    exit(1)

# Check if SECURITY_GROUP_ID is defined and properly configured
if not hasattr(SECURITY_GROUP_ID, '__str__'):
    print("SECURITY_GROUP_ID is not defined. Please define SECURITY_GROUP_ID in your environment or script configuration.")
    exit(1)

try:
    # Try to authorize inbound SSH traffic (port 22) from the retrieved IP
    ec2_client = boto3.client('ec2')
    response = ec2_client.authorize_security_group_ingress(
        GroupId=SECURITY_GROUP_ID,
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22,
        CidrIp=f'{PUBLIC_IP}/32'
    )
    print("Authorized SSH traffic")
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
    # Try to authorize inbound HTTPS traffic (port 443) from the retrieved IP
    response = ec2_client.authorize_security_group_ingress(
        GroupId=SECURITY_GROUP_ID,
        IpProtocol='tcp',
        FromPort=443,
        ToPort=443,
        CidrIp=f'{PUBLIC_IP}/32'
    )
    print("Authorized HTTPS traffic")
except NoCredentialsError as e:
    print(f"AWS credentials are not available or incomplete: {e}")
    exit(1)
except PartialCredentialsError as e:
    print(f"Incomplete AWS credentials provided: {e}")
    exit(1)
except Exception as e:
    print(f"An error occurred while authorizing HTTPS ingress: {e}")
    exit(1)
