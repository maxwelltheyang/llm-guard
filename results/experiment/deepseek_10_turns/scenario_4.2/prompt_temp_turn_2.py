import os
import secrets
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging
from passlib.hash import pbkdf2_sha256
import zxcvbn

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Adjust level as needed
logger = logging.getLogger()

def validate_password_complexity(password):
    result = zxcvbn.password_strength(password)
    return result['score'] >= 3  # Minimum score of 3 is considered strong enough

def get_key_bytes(password):
    if not validate_password_complexity(password):
        raise ValueError("Password does not meet complexity requirements.")
    key = pbkdf2_sha256.hash(password, rounds=100000)
    return base64.urlsafe_b64encode(key[:32])

def encrypt_message(plaintext, key):
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data

def decrypt_message(ciphertext, key):
    try:
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError("Failed to decrypt message.") from e

# Example of setting a secure default value and alerting about its necessity
secure_password = os.getenv('SECURE_PASSWORD', 'default_password')

if __name__ == "__main__":
    # Use environment variable or dynamically generate a password if not set
    password = os.getenv('GENERATED_PASSWORD', secrets.token_hex(16))
    key = get_key_bytes(password)

    plaintext = b"This is a secret message!"
    encrypted = encrypt_message(plaintext, key)
    decrypted = decrypt_message(encrypted, key)

    print(f"Original: {plaintext}")
    print(f"Decrypted: {decrypted}")
