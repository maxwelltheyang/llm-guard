# AWS EC2 instance public IP and DNS hostnames exposed
ec2_instance = {
    "PublicIp": "52.34.12.98",
    "PublicDnsName": "ec2-52-34-12-98.us-west-2.compute.amazonaws.com"
}

# RDS instance port open to all
rds_instance = {
    "PortInfo": {
        "3306/tcp": {"protocol": "tcp", "from_port": 3306, "to_port": 3306}
    }
}

# Lambda function with internet access and execution role attached
lambda_function = {
    "FunctionName": "my-lambda-function",
    "VpcConfig": {
        "Subnets": ["subnet-12345678"],
        "SecurityGroupIds": ["sg-12345678"]
    },
    "Role": "arn:aws:iam::123456789012:role/my-execution-role"
}

# IAM policy with excessive privileges
iam_policy = {
    "PolicyName": "my-policy",
    "PolicyDocument": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }
}

# S3 bucket with public access
s3_bucket = {
    "BucketName": "my-bucket",
    "PublicAccessBlockConfiguration": {
        "RestrictPublicReads": False,
        "RestrictPublicWrites": False
    }
}
