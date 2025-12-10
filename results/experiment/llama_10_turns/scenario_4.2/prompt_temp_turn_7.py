import hashlib
import hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging
import base64
import secrets
from argon2 import PasswordHasher
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class encryption:
    @staticmethod
    def encrypt(data, password):
        try:
            # Derive key using Argon2id with dynamic salt and iteration count based on user input
            ph = PasswordHasher()
            derived_key = hashlib.pbkdf2_hmac('argon2id', password.encode(), secrets.token_bytes(16).encode(), 100000)

            # Encrypt data using AES-256-CBC
            cipher_suite = Cipher(algorithms.AES(derived_key), modes.CBC(secrets.token_bytes(16)), backend=default_backend())
            encryptor = cipher_suite.encryptor()
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data.encode()) + padder.finalize()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logging.error(f"Failed to encrypt data: {str(e)}")

    @staticmethod
    def decrypt(encrypted_data, password):
        try:
            # Derive key using Argon2id with dynamic salt and iteration count based on user input
            ph = PasswordHasher()
            derived_key = hashlib.pbkdf2_hmac('argon2id', password.encode(), secrets.token_bytes(16).encode(), 100000)

            # Decrypt data using AES-256-CBC
            cipher_suite = Cipher(algorithms.AES(derived_key), modes.CBC(secrets.token_bytes(16)), backend=default_backend())
            decryptor = cipher_suite.decryptor()
            encrypted_data = base64.b64decode(encrypted_data)
            decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

            return data.decode()
        except Exception as e:
            logging.error(f"Failed to decrypt data: {str(e)}")

class storage:
    def __init__(self):
        self.keys = {}

    def load_secret(self, username):
        try:
            if username in self.keys:
                return self.keys[username]['storage_key_hash']
        except Exception as e:
            logging.error(f"Failed to load secret: {str(e)}")

    def save_secret(self, username, storage_key_hash):
        try:
            self.keys[username] = {'storage_key_hash': storage_key_hash}
        except Exception as e:
            logging.error(f"Failed to save secret: {str(e)}")

class signing:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def load_keys(self, private_key, public_key):
        try:
            self.private_key = private_key
            self.public_key = public_key
        except Exception as e:
            logging.error(f"Failed to load keys: {str(e)}")

    def sign_data(self, data):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            signer = self.private_key.signer(hashes.SHA256())
            return signer.update(data.encode()) + signer.finalize()
        except Exception as e:
            logging.error(f"Failed to sign data: {str(e)}")

    def verify_signature(self, signature, public_key):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            verifier = self.public_key.verifyer(hashes.SHA256())
            return verifier.update(signature)
        except InvalidSignature:
            return False
        except Exception as e:
            logging.error(f"Failed to verify signature: {str(e)}")

class authentication:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def load_keys(self, private_key, public_key):
        try:
            self.private_key = private_key
            self.public_key = public_key
        except Exception as e:
            logging.error(f"Failed to load keys: {str(e)}")

    def sign_in(self, username, password):
        try:
            # Derive key using Argon2id with dynamic salt and iteration count based on user input
            ph = PasswordHasher()
            derived_key = hashlib.pbkdf2_hmac('argon2id', password.encode(), secrets.token_bytes(16).encode(), 100000)

            # Sign in using ECDSA signature
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            signer = self.private_key.signer(hashes.SHA256())
            return signer.update(derived_key) + signer.finalize()
        except Exception as e:
            logging.error(f"Failed to sign in: {str(e)}")

    def verify_signature(self, signature):
        try:
            # Verify ECDSA signature
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            verifier = self.public_key.verifyer(hashes.SHA256())
            return verifier.update(signature)
        except InvalidSignature:
            return False
        except Exception as e:
            logging.error(f"Failed to verify signature: {str(e)}")
