import hashlib
import hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import logging
import os
import pyhsm
import secrets
import getpass
import configparser
import pathlib
import time
import uuid
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

# Use environment variables to control debug mode
if os.getenv('FLASK_DEBUG', default='False') == 'True':
    app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False

class KeyDeriver:
    def __init__(self, salt_length=16, key_length=32):
        self.salt_length = salt_length
        self.key_length = key_length

    def derive_key(self, password):
        import secrets  # Ensure we have access to secrets module
        if sys.platform == 'win32':  # Windows has limited entropy
            iterations = int(secrets.SystemRandom().randint(50000, 200000))  
        else:
            iterations = int(secrets.SystemRandom().randint(1000000, 3000000))

        salt = secrets.token_bytes(self.salt_length)
        try:
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, self.key_length)
        except Exception as e:
            logging.error("Failed to derive key: %s", str(e))

class KeyStorage:
    def __init__(self):
        self.keys = {}

    def store_key(self, ip_address, derived_key):
        # Use encryption at rest with PBKDF2 or Argon2
        import argon2  # Python's built-in Argon2 implementation
        hashed_password = argon2.hash(derived_key.hex(), salt=None, hash_length=32)
        storage_file = pathlib.Path(f'{ip_address}_key.dat')
        with open(storage_file, 'wb') as f:
            f.write(hashed_password)

    def get_key(self, ip_address):
        storage_file = pathlib.Path(f'{ip_address}_key.dat')
        if storage_file.exists():
            return self._decrypt_key(storage_file.read_bytes())
        else:
            return None

    @staticmethod
    def _decrypt_key(encrypted_key):
        import argon2  # Python's built-in Argon2 implementation
        try:
            return argon2.verify(encrypted_key.hex(), '', salt=None)
        except Exception as e:
            logging.error("Failed to decrypt key: %s", str(e))

class AESEncryption:
    def __init__(self, derived_key):
        self.key = hashlib.sha256(derived_key.encode()).digest()
        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(b'\0' * 16), backend=default_backend())

    def encrypt(self, data):
        if not isinstance(data, bytes):
            raise TypeError('Data must be of type bytes')

        try:
            encryptor = self.cipher.encryptor()
            return encryptor.update(data) + encryptor.finalize()
        except Exception as e:
            logging.error("Failed to encrypt data: %s", str(e))

    def decrypt(self, encrypted_data):
        if not isinstance(encrypted_data, bytes):
            raise TypeError('Data must be of type bytes')

        try:
            decryptor = self.cipher.decryptor()
            return decryptor.update(encrypted_data) + decryptor.finalize()
        except Exception as e:
            logging.error("Failed to decrypt data: %s", str(e))

if __name__ == '__main__':
    app.run()
