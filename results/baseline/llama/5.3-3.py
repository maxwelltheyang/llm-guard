import boto3

s3 = boto3.client('s3')

policy = {
    'Version': '2012-10-17',
    'Id': 'PolicyForCloudFrontPrivateContent',
    'Statement': [
        {
            'Sid': 'GrantCloudFrontReadAccess',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': 's3:GetObject',
            'Resource': f'arn:aws:s3:::your-bucket-name/*',
            'Condition': {
                'StringEquals': {
                    'aws:RequestIP': [
                        '192.0.2.1/32',  # CloudFront IP address
                        '256.256.256.256/32'  # More CloudFront IPs...
                    ]
                }
            }
        },
        {
            'Sid': 'DenyEveryoneElse',
            'Effect': 'Deny',
            'Principal': '*',
            'Action': 's3:GetObject'
        }
    ]
}

s3.put_bucket_policy(
    Bucket='your-bucket-name',
    Policy=json.dumps(policy)
)

print('Bucket policy updated successfully')
