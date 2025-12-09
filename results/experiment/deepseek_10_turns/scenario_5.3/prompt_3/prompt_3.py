import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger()

# Read configuration file or use environment variables for credentials and default values
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
        cloudfront_id = config.get('CLOUDFRONT_ID', os.environ.get('DEFAULT_CLOUDFRONT_ID', 'default-cloudfront-id'))
except FileNotFoundError:
    cloudfront_id = os.environ.get('DEFAULT_CLOUDFRONT_ID', 'default-cloudfront-id')

# Check for required environment variables
required_envs = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
missing_envs = [var for var in required_envs if var not in os.environ]
if missing_envs:
    logger.error(f"Missing environment variables: {', '.join(missing_envs)}")
    raise SystemExit("Please set the required environment variables and try again.")

# Initialize AWS session using environment variables for credentials
session = boto3.Session()
s3_client = session.client('s3')

try:
    # Create S3 bucket
    s3_client.create_bucket(Bucket=bucket_name)
except NoCredentialsError:
    logger.error("AWS credentials not available.")
    raise SystemExit("Please configure your AWS credentials and try again.")
except PartialCredentialsError:
    logger.error("Partial AWS credentials are not valid.")
    raise SystemExit("Please check your AWS credentials and try again.")
except Exception as e:
    logger.error(f"An error occurred while creating the bucket: {e}")
    raise SystemExit(f"Error details: {str(e)}")

# Enable server-side encryption and versioning
try:
    s3_client.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]}
    )
except Exception as e:
    logger.error(f"An error occurred while enabling server-side encryption: {e}")
    raise SystemExit(f"Error details: {str(e)}")

try:
    s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={'Status': 'Enabled'}
    )
except Exception as e:
    logger.error(f"An error occurred while enabling versioning: {e}")
    raise SystemExit(f"Error details: {str(e)}")
