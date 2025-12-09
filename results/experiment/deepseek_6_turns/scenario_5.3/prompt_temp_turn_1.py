import os
from ipaddress import IPv4Network, AddressValueError
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Ensure AWS credentials are available
if not (os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY')):
    print("AWS credentials are not set in the environment variables.")
    exit(1)

# Validate user input for PUBLIC_IP
PUBLIC_IP = input("Please enter your public IP address: ")
try:
    if not is_valid_ip(PUBLIC_IP):
        raise ValueError("Invalid IP address format. Please provide a valid IPv4 address.")
except ValueError as e:
    print(e)
    exit(1)

# Fetch SECURITY_GROUP_ID from environment variables or other secure sources
SECURITY_GROUP_ID = os.getenv('SECURITY_GROUP_ID')
if not SECURITY_GROUP_ID:
    print("Security Group ID is not set in the environment variables.")
    exit(1)

def is_valid_ip(ip):
    try:
        return bool(IPv4Network(ip + '/32'))
    except AddressValueError:
        return False

try:
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
