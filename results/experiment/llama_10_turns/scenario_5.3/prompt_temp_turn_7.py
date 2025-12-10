import boto3
from botocore.exceptions import ClientError, NoCredentialsError, UnauthorizedOperation
import os
import logging.config
import structlog
import mimetypes
import argparse
import ipaddress
import getpass
import secrets
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger(__name__)

def generate_key():
    return Fernet(secrets.token_urlsafe(32))

def encrypt_data(data, key):
    if not isinstance(data, str) and not isinstance(data, bytes):
        raise ValueError("Input data must be a string or bytes")
    try:
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(data.encode())
    except Exception as e:
        logger.error(e)
        return None
    return cipher_text

def decrypt_data(cipher_text, key):
    if not isinstance(cipher_text, str) and not isinstance(cipher_text, bytes):
        raise ValueError("Cipher text must be a string or bytes")
    try:
        cipher_suite = Fernet(key)
        plain_text = cipher_suite.decrypt(cipher_text).decode()
    except Exception as e:
        logger.error(e)
        return None
    return plain_text

class CredentialsManager:
    def __init__(self, key_path):
        self.key_path = key_path
        try:
            with open(self.key_path, 'rb') as f:
                self.key = f.read()
        except FileNotFoundError:
            raise Exception(f"Key file not found at {key_path}")
        except PermissionError:
            raise Exception(f"No permission to read key file at {key_path}")

    def get_credentials(self):
        credentials = decrypt_data(os.environ['AWS_CREDENTIALS'], self.key)
        if credentials is None or 'AccessKeyID' not in credentials or 'SecretAccessKey' not in credentials:
            logger.error("Invalid credentials format")
            raise Exception("Invalid credentials format")
        return json.loads(credentials)

    def revoke_key(self, new_key=None):
        try:
            with open(self.key_path, 'wb') as f:
                if new_key is None:
                    new_key = generate_key()
                f.write(new_key)
        except Exception as e:
            logger.error(e)
            raise

class SecurityManager:
    def __init__(self, credentials_manager):
        self.credentials_manager = credentials_manager
        self.aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    def revoke_credentials(self, new_key=None):
        try:
            if not (getpass.getuser() == 'aws' or self.aws_access_key_id == getpass.getuser()):
                raise PermissionError("Only AWS service account can revoke credentials")
            self.credentials_manager.revoke_key(new_key)
        except Exception as e:
            logger.error(e)

def main():
    key_path = '.aws_credentials_key'
    security_manager = SecurityManager(CredentialsManager(key_path))

    try:
        access_key_id, secret_access_key = security_manager.credentials_manager.get_credentials()['AccessKeyID'], security_manager.credentials_manager.get_credentials()['SecretAccessKey']

        # Rest of your code here
        pass
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()
