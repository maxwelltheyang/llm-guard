import json
import boto3
from aws_cdk import core, aws_s3 as s3

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket with block public access and server-side encryption configuration
        s3_bucket = s3.Bucket(self, "MyWebAssetsBucket",
                               block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                               removal_policy=core.RemovalPolicy.DESTROY)

        # Enforce server-side encryption for all objects in the bucket
        s3_bucket.add_to_resource_policy(aws_iam.PolicyStatement(
            actions=["s3:*"],
            effect=aws_iam.Effect.DENY,
            principals=[aws_iam.AnyPrincipal()],
            resources=["arn:aws:s3:::my-web-assets-bucket/*"],
            conditions={
                "Bool": {"aws:SecureTransport": "false"}
            }
        ))

# Define the stack and app
app = core.App()
env = core.Environment(account='<AWS-ACCOUNT-ID>', region='<AWS-REGION>')
MyStack(app, "my-web-assets-stack", env=env)

# Output the bucket name for easy access
core.CfnOutput(self, 'BucketName', value=s3_bucket.bucket_name)
