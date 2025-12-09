import json
import boto3
from aws_cdk import core, aws_s3 as s3, aws_iam as iam, aws_cloudfront as cloudfront

class MyStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket with block public access and server-side encryption configuration
        s3_bucket = s3.Bucket(self, "MyWebAssetsBucket",
                               block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                               removal_policy=core.RemovalPolicy.DESTROY)

        # Add a bucket policy to allow CloudFront access
        cloudfront_origin_id = "myCloudFrontOrigin"
        s3_bucket.add_to_resource_policy(aws_iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[f"{s3_bucket.bucket_arn}/*"],
            principals=[aws_iam.CanonicalUserPrincipal(get_caller_identity().user_id)]
        ))

# Define the stack and app
app = core.App()
env = core.Environment(account='<AWS-ACCOUNT-ID>', region='<AWS-REGION>')
MyStack(app, "my-web-assets-stack", env=env)

# Output the bucket name for easy access
core.CfnOutput(self, 'BucketName', value=s3_bucket.bucket_name)
