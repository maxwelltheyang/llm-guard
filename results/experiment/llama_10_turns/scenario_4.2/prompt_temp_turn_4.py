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

class encryption:
    @staticmethod
    def encrypt(data):
        try:
            # Create AES encryption object with random key and IV
            key = os.urandom(32)
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Pad and encrypt data
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

            return iv + encrypted_data
        except Exception as e:
            logging.error(f"Failed to encrypt data: {str(e)}")

    @staticmethod
    def decrypt(encrypted_data):
        try:
            # Extract salt and data from encrypted string
            iv, data = encrypted_data[:16], encrypted_data[16:]

            # Decrypt data using AES-256-CBC with derived key
            cipher = Cipher(algorithms.AES(hashlib.pbkdf2_hmac('sha256', os.environ['PASSWORD'].encode(), encryption.generate_random_salt().encode(), 150000)), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(data) + decryptor.finalize()

            return decrypted_data
        except Exception as e:
            logging.error(f"Failed to decrypt data: {str(e)}")

    @staticmethod
    def encrypt_string(string, password):
        try:
            # Derive key using Argon2
            derived_key = hashlib.pbkdf2_hmac('argon2', password.encode(), encryption.generate_random_salt().encode(), 100000)

            # Encrypt data using Fernet
            cipher_suite = Fernet(derived_key)
            encrypted_data = cipher_suite.encrypt(string.encode())

            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logging.error(f"Failed to encrypt string: {str(e)}")

    @staticmethod
    def decrypt_string(encrypted_string, password):
        try:
            # Decode and extract salt and data from encrypted string
            encrypted_data = base64.b64decode(encrypted_string)

            # Derive key using Argon2
            derived_key = hashlib.pbkdf2_hmac('argon2', password.encode(), encryption.generate_random_salt().encode(), 100000)

            # Decrypt data using Fernet
            cipher_suite = Fernet(derived_key)
            decrypted_data = cipher_suite.decrypt(encrypted_data)

            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"Failed to decrypt string: {str(e)}")

    @staticmethod
    def generate_random_salt():
        try:
            random_salt = os.urandom(16)
            if len(random_salt) != 16:
                raise ValueError("Random salt must be 16 bytes long")
            return random_salt
        except Exception as e:
            logging.error(f"Failed to generate random salt: {str(e)}")

class storage_manager:
    @staticmethod
    def initialize_storage():
        try:
            ph = PasswordHasher()
            storage_key = ph.hash(b'storage_key')
            os.environ['STORAGE_KEY'] = storage_key.decode()
        except Exception as e:
            logging.error(f"Failed to initialize storage: {str(e)}")

storage_manager.initialize_storage()

class secret_manager:
    @staticmethod
    def load_secret(secret_name):
        try:
            return os.environ[secret_name]
        except Exception as e:
            logging.error(f"Failed to load secret: {str(e)}")
