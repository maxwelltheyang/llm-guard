import boto3
from botocore.config import Config

# Create a session using Amazon S3
s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

# Specify the bucket name
bucket_name = 'your-bucket-name'

# Set up public access block configuration
public_access_block_configuration = {
    'BlockPublicAcls': True,
    'IgnorePublicAcls': True,
    'BlockPublicPolicy': True,
    'RestrictPublicBuckets': True
}

# Apply the public access block configuration to the bucket
s3.put_public_access_block(Bucket=bucket_name, PublicAccessBlockConfiguration=public_access_block_configuration)

# Enable encryption for all objects in the bucket
encryption_configuration = {
    'ServerSideEncryptionConfiguration': {
        'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]
    }
}

# Apply the encryption configuration to the bucket
s3.put_bucket_encryption(Bucket=bucket_name, ServerSideEncryptionConfiguration=encryption_configuration)
