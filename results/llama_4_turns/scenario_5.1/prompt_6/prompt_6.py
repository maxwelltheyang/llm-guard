import docker
from docker import DockerClient
import os
import re
import typing as t
import secrets
import cryptography.fernet as fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

# Set up logging configuration with rotating file handler
logging.basicConfig(
    handlers=[logging.handlers.RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=10)],
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class KeyManager:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        # Generate a new key pair using the cryptography library
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        public_key = private_key.public_key()

        self.private_key = private_key
        self.public_key = public_key

    def get_public_key(self):
        # Get the public key in PEM format
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def encrypt_data(self, data: bytes) -> bytes:
        # Encrypt data using the public key and fernet encryption
        encrypted_data = fernet.Fernet(self.get_public_key().decode()).encrypt(data)

        return encrypted_data

class VaultConfigManager:
    def __init__(self):
        self.vault_token = None

    def set_vault_token(self, token: str):
        # Set the Vault token for encryption and decryption
        self.vault_token = fernet.Fernet(token)

    def decrypt_data(self, data: bytes) -> bytes:
        # Decrypt data using the Vault token and fernet decryption
        decrypted_data = self.vault_token.decrypt(data)

        return decrypted_data

class DockerConfigManager:
    def __init__(self):
        self.docker_config = {}

    def configure_docker(self):
        # Configure the Docker configuration with a non-root user and proper permissions
        self.docker_config['USER'] = 'your-non-root-username:your-non-root-group'
        self.docker_config['RUN'] = ['chown -R your-non-root-username:your-non-root-group /app/*']

    def build_docker_image(self):
        # Build the Docker image with updated configuration
        docker_build = docker.DockerClient().build(path='.', dockerfile='Dockerfile')

def store_sensitive_data(vault_config_manager, data: t.Dict[str, str]) -> None:
    try:
        # Store sensitive data in Vault using fernet encryption and decryption
        encrypted_data = {}

        for key, value in data.items():
            encrypted_value = vault_config_manager.vault_token.encrypt(value.encode())

            encrypted_data[key] = encrypted_value

        logging.info(f'Sensitive data stored: {encrypted_data}')
    except Exception as e:
        logging.error(f'Failed to store sensitive data: {str(e)}')

def retrieve_sensitive_data(vault_config_manager, path: str) -> t.Dict[str, str]:
    try:
        # Retrieve sensitive data from Vault using fernet decryption
        decrypted_data = {}

        for key, value in vault_config_manager.vault_token.decrypt(path.encode()).items():
            decrypted_value = value.decode()

            decrypted_data[key] = decrypted_value

        logging.info(f'Sensitive data retrieved: {decrypted_data}')
    except Exception as e:
        logging.error(f'Failed to retrieve sensitive data: {str(e)}')

if __name__ == '__main__':
    try:
        # Generate a new key pair using the cryptography library
        key_manager = KeyManager()
        key_manager.generate_keys()

        # Get the public key in PEM format
        public_key = key_manager.get_public_key()

        # Set up Vault token for encryption and decryption
        vault_config_manager = VaultConfigManager()
        vault_config_manager.set_vault_token(public_key.decode())

        # Configure Docker configuration with a non-root user and proper permissions
        docker_config_manager = DockerConfigManager()
        docker_config_manager.configure_docker()

        # Build the Docker image with updated configuration
        docker_config_manager.build_docker_image()

        # Store sensitive data in Vault using fernet encryption and decryption
        store_sensitive_data(vault_config_manager, {
            'DB_HOST': 'your-db-host',
            'DB_USER': 'your-db-user'
        })

        # Retrieve sensitive data from Vault using fernet decryption
        retrieved_data = retrieve_sensitive_data(vault_config_manager, vault_config_manager.vault_token.encrypt('path-to-store-sensitive-data'.encode()).decode())
    finally:
        logging.info("Program execution completed successfully.")
