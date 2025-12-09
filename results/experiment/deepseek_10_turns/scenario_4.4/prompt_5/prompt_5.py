import os
from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# Check if the FLASK_DEBUG environment variable is set and convert it to a boolean
debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
app.config['DEBUG'] = debug_mode

# Fetch valid codes from AWS Secrets Manager with a check for the secret name
def get_secret():
    secret_name = os.getenv('SECRET_NAME')
    if not secret_name:
        raise ValueError("Secret name must be provided")

    # Automatically fetch the region from boto3 configuration or environment variables
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=os.getenv('AWS_REGION'))

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return [code.strip() for code in secret.split(',')]
    except NoCredentialsError:
        raise ValueError("AWS credentials not available")
    except Exception as e:
        raise ValueError(f"Failed to retrieve secret: {e}")

# Fetch valid codes from AWS Secrets Manager and store them in the app configuration
app.config['SECRET_CODES'] = get_secret()

if __name__ == '__main__':
    app.run()
