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
from logging.handlers import RotatingFileHandler
import hvac

# Set up logging configuration
logging_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'your-logs-file.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 10,
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
}

logging.config.dictConfig(logging_config)

# Load Vault token from secure storage or environment variable
vault_token = os.environ.get('VAULT_TOKEN')  # Load from environment variable

# Initialize HVAC client with Vault token
hvac_client = hvac.Client(url='your-vault-url', token=vault_token)

# Define a function to securely store sensitive data in Vault as secrets
def store_sensitive_data(data: dict) -> None:
    try:
        # Create or update a secret in Vault using the `secrets.kv.v2.create_or_update_secret` method
        hvac_client.secrets.kv.v2.create_or_update_secret(
            path='your-path-to-store-sensitive-data',
            secret=data
        )
    except Exception as e:
        logging.error(f"Failed to store sensitive data in Vault: {str(e)}")
        raise

# Define a function to securely retrieve sensitive data from Vault as secrets
def retrieve_sensitive_data(path: str) -> dict:
    try:
        # Retrieve the secret from Vault using the `secrets.kv.v2.read_secret_version` method
        secret = hvac_client.secrets.kv.v2.read_secret_version(
            path=path
        )

        # Return the decrypted data as a dictionary
        return secret.data.data.decode()
    except Exception as e:
        logging.error(f"Failed to retrieve sensitive data from Vault: {str(e)}")
        raise

# Define a function to create and configure a non-root user for the service in Docker
def create_non_root_user() -> None:
    try:
        # Create a new non-root user with specified username, group, and permissions
        dockerfile_content = f"""
            FROM python:3.9-slim-buster

            # Set working directory
            WORKDIR /app

            # Copy application code
            COPY . .

            # Expose required ports
            EXPOSE 80

            # Run the command to start the service in the background
            CMD ["python", "run.py"]

            # Configure non-root user and file permissions
            USER your-non-root-username:your-non-root-group
            RUN chown -R your-non-root-username:your-non-root-group /app/*
        """

        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)

        # Build the Docker image with updated Dockerfile content
        docker_build = docker.DockerClient().build(path='.', dockerfile='Dockerfile')
    except Exception as e:
        logging.error(f"Failed to create non-root user in Docker: {str(e)}")
        raise

# Define a function to build and run the Docker container with specified configuration
def build_docker_image(docker_config: dict) -> None:
    try:
        # Build the Docker image with updated configuration
        docker_build = docker.DockerClient().build(path='.', dockerfile='Dockerfile')

        # Run the Docker container with specified configuration
        docker_run = docker.DockerClient().create_container(
            'your-docker-image-name',
            command=['python', 'run.py'],
            environment=docker_config
        )
    except Exception as e:
        logging.error(f"Failed to build and run Docker container: {str(e)}")
        raise

# Example usage of improved code
if __name__ == '__main__':
    try:
        # Store sensitive data in Vault as secrets
        store_sensitive_data({
            'DB_HOST': fernet.Fernet(vault_token).decrypt('your-db-host').decode(),
            'DB_USER': fernet.Fernet(vault_token).decrypt('your-db-user').decode(),
            'API_KEY': fernet.Fernet(vault_token).decrypt('your-api-key').decode()
        })

        # Retrieve sensitive data from Vault as secrets
        retrieved_data = retrieve_sensitive_data('your-path-to-store-sensitive-data')

        # Log any remaining exceptions
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
    finally:
        logging.info("Program execution completed successfully.")
