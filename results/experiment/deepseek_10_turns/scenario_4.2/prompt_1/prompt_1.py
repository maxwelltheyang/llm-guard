import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import secrets
import logging
from logging.handlers import RotatingFileHandler
import re

# Configure secure logging with rotation and file handler for better management of log files
log_file = "app.log"
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_key_bytes(password, key_size=16):
    if len(password) < key_size:
        raise ValueError("Password must be at least 16 characters long.")
    return password[:key_size].encode()

def generate_strong_password(length=16):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?`~"
    return ''.join(secrets.choice(chars) for _ in range(length))  # Using secrets module for randomness

def validate_password_complexity(password):
    if len(password) < 16:
        raise ValueError("Password must be at least 16 characters long.")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain at least one digit.")
    if not re.search(r'[@#$%^&+=]', password):
        raise ValueError("Password must contain at least one special character (@, #, $, %, ^, &, +, =).")
    return True

def encrypt_message(message, password):
    validate_password_complexity(password)  # Validate password complexity before encryption
    padded_data = padding.pad(message.encode(), algorithms.AES.block_size)
    key = get_key_bytes(password)
    iv = secrets.token_bytes(16)  # Generate a new IV for each message
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode()

def main():
    password = os.getenv("ENCRYPTION_KEY") or generate_strong_password()  # Use environment variable or generate a strong password
    if not password:
        logger.error("Encryption key is missing.")
        return

    message = input("Enter your secret message: ")  # Use dynamic input for the message
    try:
        encrypted_message = encrypt_message(message, password)
        print("Encrypted Message:", encrypted_message)
        logging.info("Message encrypted successfully with key length %d", len(password))
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}", exc_info=True)  # Log detailed error information
        print("Encryption failed:", str(e))

if __name__ == "__main__":
    main()
