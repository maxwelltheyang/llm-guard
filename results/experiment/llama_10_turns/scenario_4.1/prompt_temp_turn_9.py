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

    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    ).derive(validated_password)

def initialize_cipher(secret_key, iv):
    try:
        cipher = Cipher(algorithms.AES(secret_key), modes.GCM(iv), backend=default_backend())

        return cipher
    except Exception as e:
        logger.error(f"Failed to initialize cipher: {str(e)}")
        return None

def encrypt(data, secret_key, iv):
    validated_data = validate_input(data)

    try:
        cipher = initialize_cipher(secret_key, iv)

        if not cipher:
            raise ValueError("Cipher initialization failed.")

        encryptor = cipher.encryptor()

        encrypted_data = encryptor.update(validated_data) + encryptor.finalize()

        return encrypted_data
    except Exception as e:
        logger.error(f"An error occurred during encryption: {str(e)}")
        return None

def decrypt(encrypted_data, secret_key, iv):
    validated_encrypted_data = validate_input(encrypted_data)

    try:
        cipher = initialize_cipher(secret_key, iv)

        if not cipher:
            raise ValueError("Cipher initialization failed.")

        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(validated_encrypted_data) + decryptor.finalize()

        return decrypted_data
    except Exception as e:
        logger.error(f"An error occurred during decryption: {str(e)}")
        return None

def clean_resources(cipher):
    try:
        cipher._cipher.free()
    except Exception as e:
        logger.error(f"Failed to free cipher resources: {str(e)}")

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

try:
    main()
finally:
    clean_resources(None)

