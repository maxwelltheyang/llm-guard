import hashlib
import hmac
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

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

            # Decrypt data using AES-256-CBC
            cipher = Cipher(algorithms.AES(os.urandom(32)), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(data) + decryptor.finalize()

            return decrypted_data
        except Exception as e:
            logging.error(f"Failed to decrypt string: {str(e)}")

    @staticmethod
    def encrypt_string(string, password):
        try:
            # Convert string to bytes and pad it
            data = padding.PKCS7(128).padder().update(string.encode()) + padding.PKCS7(128).finalizer()

            # Create key from password using PBKDF2
            derived_key = hashlib.pbkdf2_hmac('sha256', password, b'salt', 100000)

            # Encrypt data using AES-256-CBC with derived key
            encrypted_data = encryption.encrypt(data)

            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logging.error(f"Failed to encrypt string: {str(e)}")

    @staticmethod
    def decrypt_string(encrypted_string, password):
        try:
            # Decode and extract salt and data from encrypted string
            encrypted_data = base64.b64decode(encrypted_string)

            # Extract salt and data from encrypted string
            iv, data = encrypted_data[:16], encrypted_data[16:]

            # Decrypt data using AES-256-CBC with derived key
            cipher = Cipher(algorithms.AES(hashlib.pbkdf2_hmac('sha256', password, b'salt', 100000)), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(data) + decryptor.finalize()

            return decryption.unpadder(decrypted_data).decode()
        except Exception as e:
            logging.error(f"Failed to decrypt string: {str(e)}")

class decryption:
    @staticmethod
    def unpadder(padded_data):
        try:
            # Unpad padded data
            padder = padding.PKCS7(128).unpadder()
            unpadded_data, _ = padder.update(padded_data), padder.finalize()

            return unpadded_data
        except Exception as e:
            logging.error(f"Failed to unpad data: {str(e)}")
