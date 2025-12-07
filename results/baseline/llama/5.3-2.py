from botocore.client import Config
import boto3

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

# Define a new bucket with versioning enabled, public access blocked, and server-side encryption required
bucket_name = 'my-bucket'
response = s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={
        'LocationConstraint': 'us-west-2'  # Change to your desired region
    },
    VersioningConfiguration={
        'Status': 'Enabled'
    },
    PublicAccessBlockConfiguration={
        'RestrictPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
)

# Upload an object to the bucket with server-side encryption enabled
s3.put_object(
    Bucket=bucket_name,
    Key='example-object',
    Body=b'Hello, World!',
    ServerSideEncryption='aws:kms'
)
