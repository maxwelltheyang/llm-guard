import os
import secrets
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import logging
from passlib.hash import pbkdf2_sha256

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Adjust level as needed
logger = logging.getLogger()

def validate_password_complexity(password):
    if len(password) < 16:
        return False
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return len(password) >= 16 and has_lowercase and has_uppercase and has_digit and has_special

def get_key_bytes(password):
    if not validate_password_complexity(password):
        raise ValueError("Password does not meet complexity requirements.")
    key = pbkdf2_sha256.hash(password, rounds=100000)
    return base64.urlsafe_b64encode(key[:32])

def encrypt_message(plaintext, key):
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext

def decrypt_message(ciphertext, key):
    try:
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise

# Example usage
if __name__ == "__main__":
    password = "your_password_here"  # Replace with a secure password or handle securely
    key = get_key_bytes(password)

    message = b"This is a secret message!"
    encrypted = encrypt_message(message, key)
    print("Encrypted:", base64.b64encode(encrypted).decode())

    try:
        decrypted = decrypt_message(encrypted, key)
        print("Decrypted:", decrypted.decode())
    except Exception as e:
        logger.error(e)
