import boto3
from botocore.exceptions import ClientError, NoCredentialsError, UnauthorizedOperation
import os
import logging
import mimetypes
import argparse
import ipaddress
import getpass
import boto3
from botocore.exceptions import NoCredentialsError
import json
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    return key

def encrypt_data(data, key):
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(data.encode())
    return cipher_text

def decrypt_data(cipher_text, key):
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(cipher_text)
    return plain_text.decode()

class CredentialsManager:
    def __init__(self, key_path):
        self.key_path = key_path
        try:
            with open(self.key_path, 'rb') as f:
                self.key = f.read()
        except FileNotFoundError:
            self.key = generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(self.key)

    def get_credentials(self):
        credentials = decrypt_data(os.environ['AWS_CREDENTIALS'], self.key)
        return json.loads(credentials)

def main():
    key_path = '.aws_credentials_key'
    credentials_manager = CredentialsManager(key_path)

    try:
        access_key_id, secret_access_key = credentials_manager.get_credentials()['AccessKeyID'], credentials_manager.get_credentials()['SecretAccessKey']

        # Rest of your code here
        pass
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    main()
