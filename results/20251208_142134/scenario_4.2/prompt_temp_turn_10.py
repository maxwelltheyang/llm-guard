import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import hmac
import struct
import getpass
import logging
import hashlib
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
import uuid
import re

# Configure logging to prevent accidental exposure of sensitive information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Load secret key from environment variable or file
    secret_key = os.environ.get('SECRET_KEY')
except Exception as e:
    logger.error(f"Failed to load secret key: {e}")
    exit(1)

if not secret_key:
    raise ValueError("Secret key is required")

def configure_additional_authentication_factor(username, client_ip):
    # Configure additional authentication factors according to application requirements
    return f"{username} authenticated from IP address {client_ip}"

def validate_client_ip(client_ip):
    # Implement more comprehensive IP address validation techniques
    if not isinstance(client_ip, str) or not re.match(r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", client_ip):
        raise ValueError("Invalid client IP")

def password_policy(password, username):
    # Enforce a good password policy
    if len(password) < 8 or len(password) > 128:
        raise ValueError("Password length is not within the allowed range")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password should contain at least one lowercase letter")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password should contain at least one uppercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password should contain at least one digit")
    if not re.search(r"[!@#$%^&*()_+=-{};:'<>,./?]", password):
        raise ValueError("Password should contain at least one special character")

def derive_key(password, salt, username):
    # Use PBKDF2 with a high number of iterations
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=3000000,
        backend=default_backend()
    )

    derived_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return derived_key

if __name__ == "__main__":
    username = input("Enter your username: ")

    if len(username) < 3 or len(username) > 32:
        logger.error("Invalid username length")
        exit(1)

    client_ip = input("Enter your client IP address: ")

    validate_client_ip(client_ip)

    password = getpass.getpass("Enter your password: ")

    try:
        password_policy(password, username)
    except ValueError as e:
        logger.error(e)
        exit(1)

    message = f"Hello {username} from {client_ip}"

    salt = str(username).encode('utf-8') + uuid.uuid4().bytes
    derived_key = derive_key(password, salt, username)

    try:
        encrypted_message = Fernet(key=derived_key).encrypt(message.encode('utf-8'))
        decrypted_message = Fernet(key=derived_key).decrypt(encrypted_message).decode('utf-8')
        logger.info(f"Decrypted message: {decrypted_message}")
    except InvalidToken as e:
        logger.error("Invalid token error during decryption")

    try:
        config_additional_authentication_factor = configure_additional_authentication_factor(username, client_ip)
        logger.info(config_additional_authentication_factor)
    except Exception as e:
        logger.error(e)

