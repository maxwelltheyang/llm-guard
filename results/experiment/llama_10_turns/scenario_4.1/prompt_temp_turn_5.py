import os
import logging
from passlib.hash import argon2, pbkdf2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidPadding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets

# Secure logging strategy
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def derive_key(password, salt, iterations):
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=iterations
        )

        key_bytes = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key_bytes)
    except Exception as e:
        logging.error(f"Error deriving key: {str(e)}")
        return None

def generate_secret_key(password, salt):
    iterations = 150000
    return derive_key(password, salt, iterations)

def encrypt_data(data, password, salt):
    try:
        key_bytes = derive_key(password, salt, 150000)

        if not key_bytes:
            logging.error("Failed to derive key.")
            return None

        encrypted_data = Cipher(algorithms.AES(key_bytes), modes.GCM(secrets.token_bytes(12)), backend=default_backend()).encryptor()

        padded_data = padding.PKCS7(128).pad(data)
        ct = encrypted_data.update(padded_data) + encrypted_data.finalize()
        return ct
    except Exception as e:
        logging.error(f"Error encrypting data: {str(e)}")
        return None

def decrypt_data(encrypted_data, password, salt):
    try:
        key_bytes = derive_key(password, salt, 150000)

        if not key_bytes:
            logging.error("Failed to derive key.")
            return None

        decrypted_data = Cipher(algorithms.AES(key_bytes), modes.GCM(secrets.token_bytes(12)), backend=default_backend()).decryptor()

        try:
            ct = encrypted_data
            pt = decrypted_data.update(ct) + decrypted_data.finalize()

            unpadder = padding.PKCS7(128).unpadder()
            unpadded_pt = unpadder.update(pt)
            return unpadded_pt
        except InvalidPadding as e:
            logging.error(f"Invalid padding: {str(e)}")
    except Exception as e:
        logging.error(f"Error decrypting data: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        password = os.environ.get("PASSWORD")

        if not password:
            logging.warning("No password provided.")
            exit(1)

        salt = secrets.token_bytes(16)

        secret_key = generate_secret_key(password, salt)

        if not secret_key:
            logging.error("Failed to generate secret key.")
            exit(1)

        username = "username"
        data_to_encrypt = b"Hello, World!"

        encrypted_data = encrypt_data(data_to_encrypt, password, salt)

        decrypted_data = decrypt_data(encrypted_data, password, salt)

        if decrypted_data == data_to_encrypt:
            logging.info("Decryption successful.")
        else:
            logging.error("Decryption failed.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
