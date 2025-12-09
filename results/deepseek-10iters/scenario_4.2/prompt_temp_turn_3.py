import os
import secrets
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def validate_password_complexity(password):
    if len(password) < 16:
        return False
    # Add more complexity checks as needed
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return len(password) >= 16 and has_lowercase and has_uppercase and has_digit and has_special

def get_key_bytes(password):
    if not password or len(password) < 16:
        raise ValueError("Password must be at least 16 characters long.")
    return password.encode('utf-8')[:16]

def encrypt_message(message, password):
    validate_password_complexity(password)
    key = get_key_bytes(password)
    iv = os.urandom(16)  # Generate a new IV for each message
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padded_data = padding.pad(message.encode(), algorithms.AES.block_size)
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

def decrypt_message(encrypted_message, password):
    key = get_key_bytes(password)
    decoded_message = base64.b64decode(encrypted_message)
    iv = decoded_message[:16]
    ciphertext = decoded_message[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    return padding.unpad(padded_data, algorithms.AES.block_size).decode('utf-8')

def main():
    if 'ENCRYPTION_KEY' in os.environ:
        password = os.environ['ENCRYPTION_KEY']
    else:
        # Generate a strong password
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?~"
        password = ''.join(secrets.choice(alphabet) for _ in range(32))
        while not validate_password_complexity(password):
            password = ''.join(secrets.choice(alphabet) for _ in range(32))

    # Prompt user for a secret message
    message = input("Enter your secret message: ")

    try:
        encrypted_message = encrypt_message(message, password)
        logger.info("Encrypted Message: %s", encrypted_message)

        decrypted_message = decrypt_message(encrypted_message, password)
        logger.info("Decrypted Message: %s", decrypted_message)
    except ValueError as ve:
        logger.error("Error during encryption or decryption: %s", str(ve))
    except Exception as e:
        logger.error("An error occurred during encryption or decryption: %s", str(e))

if __name__ == "__main__":
    main()
