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
import logging
from hvac import Client
import base64
from urllib.parse import urlparse

# Initialize logger
logging.basicConfig(level=logging.INFO)

def generate_encryption_key() -> str:
    return fernet.Fernet.generate_key()

def store_encryption_key(encryption_key: str) -> None:
    # Store the encryption key securely outside the container or in a secure storage solution like Hashicorp's Vault.
    vault_url = 'http://your-vault-instance.com'
    vault_token = 'your-vault-token'

    client = Client(url=vault_url, token=vault_token)

    try:
        secret_id = client.secrets.kv.v2.create_or_update_secret(
            path='path/to/secret',
            secret={'key': encryption_key}
        )

        stored_encryption_key = secret_id.data.kv.v2.version
        return stored_encryption_key

    except Exception as e:
        logging.error(f"An error occurred while storing the encryption key: {str(e)}")

def validate_api_key(value: str) -> bool:
    try:
        # Validate the base64-encoded API key against known patterns or restrictions.
        import base64
        api_key = base64.b64decode(value, validate=True)

        if len(api_key) < 32:
            return False

        # Add more validation logic here as per your application's requirements
        return True

    except Exception as e:
        logging.error(f"An error occurred while validating the API key: {str(e)}")
        raise

def load_environment_variables() -> t.Dict[str, str]:
    try:
        env_vars = dotenv_values()

        if 'DB_HOST' not in env_vars or 'DB_USER' not in env_vars or 'API_KEY' not in env_vars:
            raise ValueError("Missing required environment variables")

        return env_vars

    except Exception as e:
        logging.error(f"An error occurred while loading environment variables: {str(e)}")

def encrypt_environment_variables(env_vars: t.Dict[str, str], stored_encryption_key: str) -> t.Dict[str, str]:
    try:
        encryption_key_bytes = fernet.Fernet(stored_encryption_key).decrypt(stored_encryption_key.encode()).decode()

        encrypted_env_vars = {}

        for var, value in env_vars.items():
            if var == 'API_KEY':
                if validate_api_key(value):
                    api_key_bytes = fernet.Fernet(encryption_key_bytes).encrypt(value.encode())
                    encrypted_env_vars[var] = api_key_bytes.decode()
                else:
                    logging.error(f"Invalid API key: {value}")
                    raise ValueError("API key validation failed")
            else:
                encrypted_env_vars[var] = value

        return encrypted_env_vars

    except Exception as e:
        logging.error(f"An error occurred while encrypting environment variables: {str(e)}")
        raise

def build_docker_image(env_vars: t.Dict[str, str]) -> None:
    try:
        docker_client = DockerClient()
        image_name = 'app'

        # Build the Docker image
        images = docker_client.images.build(path='.', tag=image_name)

        # Remove the temporary Docker container
        for c in docker_client.containers.list():
            if c.name.startswith(image_name):
                docker_client.containers.kill(c.id)
                docker_client.containers.remove(c.id)

    except Exception as e:
        logging.error(f"An error occurred while building or removing the Docker image: {str(e)}")

def clean_up_temporary_directories(temp_dir: str) -> None:
    try:
        # Clean up temporary directories regardless of exceptions
        import os
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass

# Example usage with more specific secret generation methods
if __name__ == "__main__":
    env_vars = {
        'DB_HOST': secrets.token_urlsafe(16),
        'DB_USER': secrets.token_urlsafe(16),
        'API_KEY': secrets.token_urlsafe(32)
    }

    temp_dir = tempfile.mkdtemp()

    try:
        encryption_key = generate_encryption_key()

        stored_encryption_key = store_encryption_key(encryption_key)

        env_vars['ENCRYPTION_KEY'] = stored_encryption_key

        encrypted_env_vars = encrypt_environment_variables(env_vars, stored_encryption_key)

        build_docker_image(encrypted_env_vars)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    finally:
        clean_up_temporary_directories(temp_dir)

# More specific secret generation methods can be used here
# Example: secrets.token_hex(32), secrets.token_bytes(16), etc.
