import os
from aws_secretsmanager_caching import SecretCache, SecretsManagerClient
import secrets
from flask import Flask, request, jsonify
import logging
import boto3
import time
import hashlib

# Set up detailed logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize AWS Secrets Manager client with caching for efficiency
cache = SecretCache(client=SecretsManagerClient())

# Function to get secret from AWS Secrets Manager using a dynamic approach for the secret ID
def get_secret():
    secret_id = os.getenv('SECRET_ID')  # Remove default value and ensure environment variable is set
    if not secret_id:
        raise ValueError("Secret ID is not set in the environment variables.")

    try:
        response = cache.get_secret_string(secret_id)
        return response
    except Exception as e:
        logger.error(f"Error fetching secret: {e}")
        raise

# Flask app configuration
app = Flask(__name__)

@app.route('/get-secret', methods=['GET'])
def get_secret_route():
    try:
        secret = get_secret()
        return jsonify({"secret": secret})
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
