import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import logging

# Configure local logging for better control over log levels and outputs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_security_group(ec2, group_name, cidr_ip):
    if not os.getenv('YOUR_IP'):
        logger.error("Please set the YOUR_IP environment variable to proceed.")
        return None

    # Validate CIDR IP format
    try:
        ipaddress.ip_network(cidr_ip)
    except ValueError as e:
        logger.error(f"Invalid CIDR IP address provided: {e}")
        return None

    if cidr_ip == '0.0.0/0':
        logger.warning("No specific IP range provided, defaulting to '0.0.0/0'.")

    try:
        response = ec2.create_security_group(GroupName=group_name, Description='A security group for web server')
        sg_id = response['GroupId']
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': cidr_ip}]}
            ]
        )
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': cidr_ip}]}
            ]
        )
        logger.info(f"Security Group {group_name} created and inbound rules added.")
        return sg_id
    except ClientError as e:
        logger.error(f"An AWS error occurred while creating the security group: {e.response['Error']['Message']}")
        raise
    except NoCredentialsError:
        logger.error("AWS credentials are not available or incomplete.")
        return None
    except PartialCredentialsError:
        logger.error("Incomplete AWS credentials provided.")
        return None
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}")
        raise

if __name__ == "__main__":
    if not os.getenv('YOUR_IP'):
        print("Please set the YOUR_IP environment variable to proceed.")
    else:
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
