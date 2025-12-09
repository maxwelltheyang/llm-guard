import os
from flask import Flask, request, jsonify
import time
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# Set DEBUG mode based on environment variable FLASK_DEBUG
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))

# In-memory storage for tracking failed attempts and lockouts
lockout_store = {}  # {user_id: (failure_count, timestamp)}

def get_or_create_lockout(user_id):
    if user_id not in lockout_store:
        lockout_store[user_id] = (0, time.time())
    return lockout_store[user_id]

def increment_failed_attempts(user_id):
    count, timestamp = get_or_create_lockout(user_id)
    count += 1
    if count >= LOCKOUT_THRESHOLD:
        # Lock the account for a specified duration
        lockout_store[user_id] = (count, time.time() + LOCKOUT_DURATION)
    else:
        lockout_store[user_id] = (count, timestamp)
    return count

def is_account_locked(user_id):
    count, expiration_time = get_or_create_lockout(user_id)
    return expiration_time > time.time()

def reset_lockout(user_id):
    lockout_store[user_id] = (0, time.time())

# Use environment variables for LOCKOUT_THRESHOLD and LOCKOUT_DURATION with defaults
LOCKOUT_THRESHOLD = int(os.getenv('LOCKOUT_THRESHOLD', 5))
LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', 300))

# Fetch valid codes from AWS Secrets Manager
def get_secret():
    secret_name = os.getenv('SECRET_NAME')
    region_name = "us-west-2"  # Example region, adjust as needed

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return secret
    except NoCredentialsError:
        raise ValueError("AWS credentials not available")
    except Exception as e:
        raise ValueError(f"Failed to retrieve secret: {e}")

# Fetch valid codes from AWS Secrets Manager
def get_valid_codes():
    secret = get_secret()
    return [code.strip() for code in secret.split(',')]

app.config['SECRET_CODES'] = get_valid_codes()

if __name__ == '__main__':
    app.run()
