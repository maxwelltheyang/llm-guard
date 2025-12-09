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
        vault_client = hvac.Client(token=vault_token)
        vault_token = vault_client.auth_user_pass_login('your-vault-username', 'your-vault-password')['auth']['client_token']
    except Exception as e:
        logging.error(f"Failed to fetch or load Vault token: {str(e)}")
        raise

# Load environment variables
env_vars = dotenv_values('.env')

# Encrypt sensitive data like database credentials and API keys using Fernet encryption
encrypted_env_vars = {}
for key, value in env_vars.items():
    if 'DB_' in key or 'API_KEY' in key:
        encrypted_env_vars[key] = fernet.Fernet(vault_token).encrypt(value.encode()).decode()

# Store encrypted environment variables as secrets in Vault
stored_encrypted_env_vars = hvac.Client(token=vault_token).secrets.kv.v2.create_or_update_secret(
    path='your-encrypted-env-vars-path',
    secret=encrypted_env_vars
)

# Use the encrypted environment variables for Docker container configuration
docker_config = {
    'DB_HOST': fernet.Fernet(vault_token).decrypt(stored_encrypted_env_vars['DB_HOST'].encode()).decode(),
    'DB_USER': fernet.Fernet(vault_token).decrypt(stored_encrypted_env_vars['DB_USER'].encode()).decode(),
    'API_KEY': fernet.Fernet(vault_token).decrypt(stored_encrypted_env_vars['API_KEY'].encode()).decode()
}

# Create a non-root user for the service and configure file permissions
def create_non_root_user():
    try:
        user = 'your-non-root-username'
        group = 'your-non-root-group'

        # Use the official Python image aligned with your application's dependencies and requirements
        docker_image = 'python:3.9-slim-buster'

        # Configure the service user and file permissions correctly in the Dockerfile
        dockerfile_content = f"""
            FROM {docker_image}

            # Set working directory
            WORKDIR /app

            # Copy application code
            COPY . .

            # Expose required ports
            EXPOSE 80

            # Run the command to start the service in the background
            CMD ["python", "run.py"]

            # Configure the non-root user and file permissions
            USER {user}:{group}
            RUN chown -R {user}:{group} /app/*
        """

        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)

        # Build the Docker image with the updated Dockerfile content
        docker_build = docker.DockerClient().build(path='.', dockerfile='Dockerfile')
    except Exception as e:
        logging.error(f"Failed to create non-root user: {str(e)}")
        raise

create_non_root_user()

# Run the Docker container with the specified configuration
def build_docker_image(docker_config):
    try:
        # Build the Docker image with the updated configuration
        docker_build = docker.DockerClient().build(path='.', dockerfile='Dockerfile')

        # Run the Docker container with the specified configuration
        docker_run = docker.DockerClient().create_container(
            'your-docker-image-name',
            command=['python', 'run.py'],
            environment=docker_config
        )
    except Exception as e:
        logging.error(f"Failed to build Docker image: {str(e)}")
        raise

# Example usage of the improved code
if __name__ == '__main__':
    try:
        # Build and run the Docker container with the specified configuration
        build_docker_image(docker_config)

        # Log any remaining exceptions before they reach the top-level exception handler
        logging.exception('An unexpected error occurred')
    except Exception as e:
        # Log any remaining exceptions before they reach the top-level exception handler
        logging.error(f"An unexpected error occurred: {str(e)}")
