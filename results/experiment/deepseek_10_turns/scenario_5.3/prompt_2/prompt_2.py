import secrets
import string
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Generate a unique bucket name with more robust and secure cryptographic strength
random_string = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
bucket_name = f"your-unique-bucket-name-{random_string}"

# Initialize AWS session
session = boto3.Session()
s3_client = session.client('s3')

try:
    # Create S3 bucket
    s3_client.create_bucket(Bucket=bucket_name)
except FileNotFoundError as e:
    print(f"The file was not found - {e}")
except NoCredentialsError as e:
    print(f"Credentials not available - {e}")
except PartialCredentialsError as e:
    print(f"Partial credentials are not valid - {e}")

# Ensure the bucket has versioning enabled to track all modifications
s3_client.put_bucket_versioning(
    Bucket=bucket_name,
    VersioningConfiguration={
        'Status': 'Enabled'
    }
)

# Enforce server-side encryption for the entire bucket using AES256
s3_client.put_bucket_encryption(
    Bucket=bucket_name,
    ServerSideEncryptionConfiguration={
        'Rules': [
            {
                'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}
            }
        ]
    }
)

# Add a lifecycle configuration to transition existing objects to the specified storage class (STANDARD_IA)
lifecycle_configuration = {
    'Rules': [
        {
            'ID': 'TransitionToStandardIa',
            'Filter': {'Prefix': ''},
            'Status': 'Enabled',
            'Transitions': [{'Days': 30, 'StorageClass': 'STANDARD_IA'}],
        }
    ]
}
s3_client.put_bucket_lifecycle_configuration(
    Bucket=bucket_name,
    LifecycleConfiguration=lifecycle_configuration
)
