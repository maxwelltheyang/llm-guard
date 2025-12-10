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
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[
    logging.FileHandler('app.log'),
    logging.StreamHandler()
])

def get_environment_variable(name):
    if name in os.environ:
        return os.environ[name]
    else:
        raise ValueError(f"Environment variable '{name}' not found.")

def derive_key(password, salt, iterations=200000):
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
    secret_key = derive_key(password, salt)

    if not secret_key:
        logging.error("Failed to generate secret key.")
        raise ValueError("Failed to generate secret key.")

    return secret_key

if __name__ == "__main__":
    try:
        password = get_environment_variable("PASSWORD")

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

        encrypted_data = None
        decrypted_data = None

        try:
            iv = secrets.token_bytes(12)  # Ensure IV is properly randomized and consistent

            cipher = Cipher(algorithms.AES(secret_key), modes.GCM(iv), backend=default_backend())

            encryptor = cipher.encryptor()

            encrypted_data = encryptor.update(data_to_encrypt) + encryptor.finalize()
        except Exception as e:
            logging.error(f"An error occurred during encryption: {str(e)}")

        try:
            decryptor = cipher.decryptor()

            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

            if decrypted_data == data_to_encrypt:
                logging.info("Decryption successful.")
            else:
                logging.error("Decryption failed.")

        except Exception as e:
            logging.error(f"An error occurred during decryption: {str(e)}")

    except Exception as e:
        logging.error(f"An exception occurred: {str(e)}")

