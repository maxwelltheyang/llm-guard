import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import ipaddress
import logging

# Configure local logging for better control over log levels and outputs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_security_group(ec2, group_name, cidr_ip):
    if not os.getenv('YOUR_IP'):
        logger.error("Please set the YOUR_IP environment variable to proceed.")
        raise ValueError("Missing required environment variable: YOUR_IP")

    try:
        ipaddress.ip_network(cidr_ip)
    except ValueError as e:
        logger.error(f"Invalid CIDR IP address provided: {e}")
        raise ValueError(f"Invalid CIDR IP address: {e}")

    aws_region = os.getenv('AWS_REGION', 'us-west-2')  # Default to a specific region if not set

    try:
        session = boto3.Session(region_name=aws_region)
        ec2 = session.client('ec2')

        try:
            response = ec2.create_security_group(GroupName=group_name, Description='Security group for webserver', VpcId='your-vpc-id')
            security_group_id = response['GroupId']

            # Authorize the ingress rule to allow traffic on port 80 and 443
            ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': cidr_ip}]}
                ]
            )

            ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': cidr_ip}]}
                ]
            )

            logger.info(f"Security group {group_name} created successfully with ID: {security_group_id}")
            return security_group_id
        except ClientError as e:
            logger.error(f"Failed to create security group: {e}")
            raise e
    except NoCredentialsError:
        logger.critical("AWS credentials are not available or incomplete.")
        raise SystemExit("Missing AWS credentials")
    except PartialCredentialsError:
        logger.critical("Incomplete AWS credentials provided.")
        raise SystemExit("Incomplete AWS credentials")
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}")
        raise

if __name__ == "__main__":
    try:
        if not os.getenv('YOUR_IP'):
            raise ValueError("Missing required environment variable: YOUR_IP")

        aws_region = os.getenv('AWS_REGION', 'us-west-2')  # Default to a specific region if not set
        try:
            session = boto3.Session(region_name=aws_region)
            ec2 = session.client('ec2')
            security_group_id = create_security_group(ec2, 'webserver-sg', os.getenv('YOUR_IP'))
            if security_group_id is None:
                logger.error("Security group creation failed.")
        except NoCredentialsError:
            print("AWS credentials are not available or incomplete.")
        except Exception as e:
            logger.critical(f"Unexpected error occurred: {e}")
    except ValueError as ve:
        print(ve)
