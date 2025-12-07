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

# Initialize logger
logging.basicConfig(level=logging.INFO)

def generate_encryption_key() -> str:
    return fernet.Fernet.generate_key()

def store_encryption_key(encryption_key: str) -> None:
    # Store the encryption key securely outside the container or in a secure storage solution like Hashicorp's Vault.
    pass

def encrypt_environment_variables(env_vars: t.Dict[str, str], encryption_key: str) -> t.Dict[str, str]:
    cipher_suite = fernet.Fernet(encryption_key)

    encrypted_env_vars = {}

    for key, value in env_vars.items():
        if key == 'API_KEY':
            encrypted_value = cipher_suite.encrypt(value.encode())
            encrypted_env_vars[key] = encrypted_value.decode()
        else:
            encrypted_env_vars[key] = value

    return encrypted_env_vars

def load_environment_variables() -> t.Dict[str, str]:
    try:
        env_vars = dotenv_values()

        # Check if all required environment variables are present
        required_env_vars = ['DB_HOST', 'DB_USER', 'API_KEY']
        for var in required_env_vars:
            if var not in env_vars:
                logging.error(f"Missing required environment variable: {var}")
                raise SystemExit(1)

        return env_vars

    except FileNotFoundError as e:
        logging.error(f"Failed to find .env file: {e}")
        raise SystemExit(1)

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
        logging.error(f"An error occurred while building or removing the Docker image: {e}")

def clean_up_temporary_directories(temp_dir: str) -> None:
    try:
        # Clean up temporary directories regardless of exceptions
        import os
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass

# Example usage of these functions
if __name__ == "__main__":
    env_vars = {
        'DB_HOST': secrets.token_urlsafe(16),
        'DB_USER': secrets.token_urlsafe(16),
        'API_KEY': secrets.token_urlsafe(32)
    }

    encryption_key = generate_encryption_key()
    store_encryption_key(encryption_key)
    encrypted_env_vars = encrypt_environment_variables(env_vars, encryption_key)

    temp_dir = tempfile.mkdtemp()

    try:
        build_docker_image(env_vars)
    finally:
        clean_up_temporary_directories(temp_dir)
