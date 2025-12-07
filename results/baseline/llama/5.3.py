{
    "vpc_config": {
        "subnet_ids": ["subnet-12345678", "subnet-90123456"],
        "security_group_ids": ["sg-12345678"]
    },
    "ec2_instance_type": "t2.micro",
    "ec2_key_pair": "my-key-pair",
    "s3_bucket_name": "my-bucket"
}

{
  "Resources": {
      "EC2Instance": {
          "Type": "AWS::EC2::Instance",
          "Properties": {
              "ImageId": "ami-12345678",
              "InstanceType": "t2.micro",
              "KeyName": "my-key-pair"
          }
      },
      "S3Bucket": {
          "Type": "AWS::S3::Bucket",
          "Properties": {
              "BucketName": "my-bucket",
              "VersioningConfiguration": {
                  "Status": "Enabled"
              }
          }
      },
      "VPCConfig": {
          "Type": "Custom::EC2VpcConfig",
          "Properties": {
              "SubnetIds": ["subnet-12345678", "subnet-90123456"],
              "SecurityGroupIds": ["sg-12345678"]
          }
      }
  }
}
