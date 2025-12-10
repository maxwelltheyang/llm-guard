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

# Secure logging strategy with encryption and secure output
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[
    logging.FileHandler('app.log'),
    logging.StreamHandler()
])
logger = logging.getLogger()

def validate_input(input_str):
    try:
        if not isinstance(input_str, str) or len(input_str) == 0:
            raise ValueError("Input must be a non-empty string.")

        # Whitelist allowed characters for username
        if any(char in input_str for char in '/\\*?"<>&|'):
            raise ValueError("Username contains invalid characters.")

        return input_str
    except Exception as e:
        logger.error(f"Invalid input: {str(e)}")
        raise

def get_environment_variable(name):
    validated_name = validate_input(name)

    if name in os.environ:
        return os.environ[name]
    else:
        logger.warning("Environment variable not found.")
        return None

def generate_salt(length=16):
    return secrets.token_bytes(length)

def derive_key(password, salt):
    validated_password = validate_input(password)
    validated_salt = validate_input(salt)

    try:
        return argon2.hash(validated_password, salt=salt, hash_function='argon2id', memory_cost=16384, iteration_count=4)
    except Exception as e:
        logger.error(f"Key derivation failed: {str(e)}")
        return None

def main():
    username = "username"
    data_to_encrypt = b"Hello, World!"

    password = get_environment_variable("PASSWORD")
    if not password:
        return

    salt = generate_salt()
    secret_key = derive_key(password, salt)

    iv = secrets.token_bytes(16)  # Ensure IV length is exactly 16 bytes for AES-256-GCM

    encrypted_data = encrypt(data_to_encrypt, secret_key, iv)

    decrypted_data = decrypt(encrypted_data, secret_key, iv)

    if decrypted_data == data_to_encrypt:
        logger.info("Decryption successful.")
    else:
        logger.error("Decryption failed.")

def clean_resources(cipher):
    try:
        cipher._cipher.free()
    except Exception as e:
        logger.error(f"Failed to free cipher resources: {str(e)}")

try:
    from cryptography.hazmat.backends import default_backend
    main()
finally:
    clean_resources(None)

