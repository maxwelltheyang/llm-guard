import docker
from docker import DockerClient
import os
import re
import typing as t
import secrets
import cryptography.fernet as fernet
from dotenv import load_dotenv, dotenv_values
import tempfile
import shutil
import logging.config
import logging.handlers
import hvac
from urllib.parse import urlparse

# Initialize logger with more robust configuration
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'app.log',
            'when': 'midnight',
            'backupCount': 30,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

# Load Vault token from secure storage or environment variable
vault_token = os.environ.get('VAULT_TOKEN')
if not vault_token:
    try:
        # Fetch Vault token securely (e.g., using a service account)
        vault_token = hvac.Client().auth_user_pass_login('your-vault-username', 'your-vault-password')
    except Exception as e:
        logging.error(f"Failed to fetch or load Vault token: {str(e)}")
        raise

# Load environment variables for configuration
env_vars = {
    'DB_HOST': os.environ.get('DB_HOST'),
    'DB_USER': os.environ.get('DB_USER'),
    'API_KEY': os.environ.get('API_KEY')
}

def load_environment_variables():
    required_env_vars = ['DB_HOST', 'DB_USER', 'API_KEY']

    for var in required_env_vars:
        if not env_vars[var]:
            logging.error(f"Missing required environment variable: {var}")
            raise ValueError(f"Missing required environment variable: {var}")

    return env_vars

env_vars = load_environment_variables()

# Generate secrets with more specific methods
if __name__ == "__main__":
    try:
        encryption_key = secrets.token_bytes(32)

        stored_encryption_key = hvac.Client(token=vault_token).secrets.kv.v2.create_or_update_secret(
            path='your-encryption-key-path',
            secret={'value': encryption_key.decode()}
        )

        env_vars['ENCRYPTION_KEY'] = stored_encryption_key

        encrypted_env_vars = {
            'DB_HOST': secrets.token_hex(32),
            'DB_USER': secrets.token_bytes(16),
            'API_KEY': secrets.token_urlsafe(32)
        }

        build_docker_image(encrypted_env_vars)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

# Dockerfile for security best practices compliance
# Use the official Python image for your application's requirements
FROM python:3.9-slim

# Set working directory and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose required ports
EXPOSE 80

# Run the command to start the service in the background
CMD ["python", "run.py"]

# Security best practices compliance:
# 1. Use a non-root user for the service (e.g., using useradd)
# 2. Set file permissions and ownership correctly (e.g., using chown, chmod)
