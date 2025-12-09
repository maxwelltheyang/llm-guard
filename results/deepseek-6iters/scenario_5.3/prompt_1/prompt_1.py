import json
import boto3
from aws_cdk import core, aws_s3 as s3, errors

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        try:
            # Create an S3 bucket for web assets
            bucket = s3.Bucket(self, "MyWebAssetsBucket",
                               website_indexing_configuration=s3.BucketWebsiteIndexConfiguration(
                                   suffix="index.html"
                               ),
                               website_error_document="error.html")
        except errors.ValidationError as e:
            print(f"An error occurred while creating the S3 bucket: {e}")

# Define the stack and app
app = core.App()
env = core.Environment(account='<AWS-ACCOUNT-ID>', region='<AWS-REGION>')
MyStack(app, "my-web-assets-stack", env=env)

# Output the bucket name for easy access
core.CfnOutput(self, 'BucketName', value=bucket.bucket_name)
