import hashlib
import hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging
import base64
import secrets
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class encryption:
    @staticmethod
    def encrypt(data, password):
        try:
            # Derive key using Argon2id with dynamic salt and iteration count based on user input
            ph = PasswordHasher()
            derived_key = hashlib.pbkdf2_hmac('argon2id', password.encode(), secrets.token_bytes(16).encode(), 100000)

            # Encrypt data using Fernet
            cipher_suite = Fernet(derived_key)
            encrypted_data = cipher_suite.encrypt(data)

            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logging.error(f"Failed to encrypt data: {str(e)}")

    @staticmethod
    def decrypt(encrypted_data, password):
        try:
            # Derive key using Argon2id with dynamic salt and iteration count based on user input
            ph = PasswordHasher()
            derived_key = hashlib.pbkdf2_hmac('argon2id', password.encode(), secrets.token_bytes(16).encode(), 100000)

            # Decrypt data using Fernet
            cipher_suite = Fernet(derived_key)
            decrypted_data = cipher_suite.decrypt(base64.b64decode(encrypted_data))

            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"Failed to decrypt data: {str(e)}")

class storage_manager:
    def __init__(self):
        self.storage_keys = {}

    def initialize_storage(self, username):
        try:
            if username not in self.storage_keys:
                # Generate random salt
                salt = secrets.token_bytes(16)

                # Derive key using PBKDF2 with SHA-512 and dynamic iteration count based on user input
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA512(),
                    length=32,
                    salt=salt,
                    iterations=int(username),
                )
                storage_key_derived = kdf.derive(b'storage_key')

                # Store the storage key hash in a secure manner (e.g., encrypted file or database)
                from cryptography.fernet import Fernet
                fernet = Fernet.from_user_password(password=username, salt=salt)
                self.storage_keys[username] = {
                    'storage_key_hash': fernet.encrypt(storage_key_derived),
                    'salt': fernet.encrypt(salt),
                }
        except Exception as e:
            logging.error(f"Failed to initialize storage: {str(e)}")

    def load_secret(self, username):
        try:
            if username in self.storage_keys:
                return self.storage_keys[username]['storage_key_hash']
        except Exception as e:
            logging.error(f"Failed to load secret: {str(e)}")
