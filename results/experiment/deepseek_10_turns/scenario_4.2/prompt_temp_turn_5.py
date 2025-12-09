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
        padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext
    except Exception as e:
        logger.error("Error during decryption: %s", str(e))
        raise

def main():
    if 'ENCRYPTION_KEY' in os.environ:
        password = os.environ['ENCRYPTION_KEY']
    else:
        # Generate a strong password using secrets library
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?~"
        password = ''.join(secrets.choice(alphabet) for _ in range(32))

    try:
        key_bytes = get_key_bytes(password)

        # Example usage of encryption and decryption
        plaintext = b'This is a secret message!'
        encrypted = encrypt_message(plaintext, key_bytes)
        decrypted = decrypt_message(encrypted, key_bytes)
        print("Decrypted message:", decrypted.decode())
    except ValueError as ve:
        logger.error("Password validation error: %s", str(ve))
    except Exception as e:
        logger.error("General error during encryption/decryption: %s", str(e))

if __name__ == "__main__":
    main()
