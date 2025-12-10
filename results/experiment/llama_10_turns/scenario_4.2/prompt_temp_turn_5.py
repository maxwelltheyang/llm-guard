import hashlib
import hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import logging
import base64
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization

class encryption:
    @staticmethod
    def encrypt(data, password):
        try:
            # Derive key using Argon2 with dynamic salt and iteration count based on user input
            ph = PasswordHasher()
            derived_key = hashlib.pbkdf2_hmac('argon2', password.encode(), os.urandom(16).encode(), 100000)

            # Encrypt data using Fernet
            cipher_suite = Fernet(derived_key)
            encrypted_data = cipher_suite.encrypt(data)

            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logging.error(f"Failed to encrypt data: {str(e)}")

    @staticmethod
    def decrypt(encrypted_data, password):
        try:
            # Derive key using Argon2 with dynamic salt and iteration count based on user input
            ph = PasswordHasher()
            derived_key = hashlib.pbkdf2_hmac('argon2', password.encode(), os.urandom(16).encode(), 100000)

            # Decrypt data using Fernet
            cipher_suite = Fernet(derived_key)
            decrypted_data = cipher_suite.decrypt(base64.b64decode(encrypted_data))

            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"Failed to decrypt data: {str(e)}")

class storage_manager:
    @staticmethod
    def initialize_storage():
        try:
            ph = PasswordHasher()
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            storage_key_derived = kdf.derive(b'storage_key')
            storage_key_hashed = ph.hash(storage_key_derived)
            os.environ['STORAGE_KEY'] = storage_key_hashed.decode()
        except Exception as e:
            logging.error(f"Failed to initialize storage: {str(e)}")

    @staticmethod
    def load_secret(secret_name):
        try:
            return os.environ[secret_name]
        except Exception as e:
            logging.error(f"Failed to load secret: {str(e)}")
