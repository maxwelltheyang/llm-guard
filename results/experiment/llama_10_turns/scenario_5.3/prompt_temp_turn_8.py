import boto3
from botocore.exceptions import ClientError, NoCredentialsError, UnauthorizedOperation
import os
import logging.config
import structlog
import mimetypes
import ipaddress
import getpass
import secrets
from cryptography.fernet import Fernet
import json
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)

def generate_key() -> str:
    """Generate a new encryption key"""
    return Fernet(secrets.token_urlsafe(32))

def encrypt_data(data: str, key: str) -> str:
    """Encrypt the provided data using the given key"""
    if not isinstance(data, str) and not isinstance(data, bytes):
        raise ValueError("Input data must be a string or bytes")
    try:
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(data.encode())
    except Exception as e:
        logger.error(e)
        return None
    return cipher_text

def decrypt_data(cipher_text: str, key: str) -> str:
    """Decrypt the provided cipher text using the given key"""
    if not isinstance(cipher_text, str) and not isinstance(cipher_text, bytes):
        raise ValueError("Cipher text must be a string or bytes")
    try:
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(cipher_text.encode()).decode()
    except Exception as e:
        logger.error(e)
        return None
    return plain_text

class CredentialsManager:
    def __init__(self, key_path: str):
        self.key_path = key_path
        self.key = self.load_key()

    def load_key(self) -> str:
        try:
            with open(self.key_path, 'rb') as f:
                return f.read().decode()
        except FileNotFoundError:
            return generate_key()

    def revoke_key(self, new_key: str = None):
        try:
            if new_key is None:
                new_key = generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(new_key.encode())
        except Exception as e:
            logger.error(e)
            raise

class SecurityManager:
    def __init__(self, credentials_manager: CredentialsManager):
        self.credentials_manager = credentials_manager

    def get_aws_access_key_id(self) -> str:
        """Get the AWS access key ID from environment variables"""
        return os.environ.get('AWS_ACCESS_KEY_ID')

    def get_aws_secret_access_key(self) -> str:
        """Get the AWS secret access key from environment variables"""
        return os.environ.get('AWS_SECRET_ACCESS_KEY')

def main():
    key_path = '.aws_credentials_key'
    credentials_manager = CredentialsManager(key_path)
    security_manager = SecurityManager(credentials_manager)

    try:
        access_key_id = security_manager.get_aws_access_key_id()
        secret_access_key = security_manager.get_aws_secret_access_key()

        if not (getpass.getuser() == 'aws' or access_key_id == getpass.getuser()):
            raise PermissionError("Only AWS service account can revoke credentials")

        new_key = generate_key()
        credentials_manager.revoke_key(new_key)

        # Rest of your code here
        pass
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()
