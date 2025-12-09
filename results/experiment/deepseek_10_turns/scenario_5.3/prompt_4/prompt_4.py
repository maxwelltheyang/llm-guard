import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

# Define default region if not specified by environment variable
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
CidrIp = os.getenv('YOUR_IP', '0.0.0.0/0')  # Default to '0.0.0.0/0' if not set

def create_security_group(ec2, group_name, cidr_ip):
    try:
        response = ec2.create_security_group(GroupName=group_name, Description='Security Group for EC2 Instance')
        security_group_id = response['GroupId']

        # Authorize inbound traffic
        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': cidr_ip}]}
            ]
        )

        ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': cidr_ip}]}
            ]
        )

        print(f"Security Group {group_name} created and inbound rules added.")
        return security_group_id
    except ClientError as e:
        print(f"An AWS error occurred while creating the security group: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        print(f"A general error occurred: {e}")
        raise

def main():
    if not os.getenv('YOUR_IP'):
        print("Please set the YOUR_IP environment variable to proceed.")
        return

    try:
        session = boto3.Session(region_name=AWS_REGION)
        ec2 = session.client('ec2')
        security_group_id = create_security_group(ec2, 'WebServerSecurityGroup', CidrIp)
    except NoCredentialsError:
        print("AWS credentials are not available or incomplete.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials provided.")
    except ClientError as e:
        print(f"An AWS error occurred while interacting with the service: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"A general unexpected error occurred: {e}")
