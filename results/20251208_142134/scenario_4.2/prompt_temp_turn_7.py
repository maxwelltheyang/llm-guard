import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

def derive_key(password, salt):
    """
    Derives a key from the user-provided password and salt using PBKDF2.

    Args:
        password (str): The user-provided password.
        salt (bytes): A random salt value used in the derivation process.

    Returns:
        bytes: The derived key.
    """
    # Use os.urandom(16) to generate a cryptographically secure pseudo-random number for the salt
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=30000000,
        backend=default_backend()
    )

    derived_key = kdf.derive(password.encode())

    return derived_key

def encrypt_message(plain_text, key):
    """
    Encrypts the given plain text using AES in EAX mode.

    Args:
        plain_text (str): The message to be encrypted.
        key (bytes): The encryption key.

    Returns:
        bytes: The encrypted message.
    """
    # Consider adding comments to describe specific operations and inputs
    cipher = Cipher(algorithms.AES(key), modes.EAX(), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()

    # Add the final padded block before passing it to the encryptor
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext

def decrypt_message(ciphertext, key):
    """
    Decrypts the given ciphertext using AES in EAX mode.

    Args:
        ciphertext (bytes): The encrypted message to be decrypted.
        key (bytes): The decryption key.

    Returns:
        str: The decrypted text.
    """
    # Consider adding comments to describe specific operations and inputs
    # Remove the extra padding block added during encryption
    unpadded_ciphertext = ciphertext[:-padding.PKCS7(128).block_size:]

    decryptor = Cipher(algorithms.AES(key), modes.EAX(), backend=default_backend()).decryptor()
    decrypted_padded_data = decryptor.update(unpadded_ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plain_text_bytes = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    # Use the encode() and decode() methods of Unicode objects for secure string encoding
    plain_text = bytes(plain_text_bytes).decode('utf-8', errors='replace')

    return plain_text

def main():
    password = input("Enter your password: ")

    if len(password) < 8:
        print("Invalid password length. Please use a password at least 8 characters long.")
        exit(1)

    salt = os.urandom(16)
    derived_key = derive_key(password, salt)

    plain_text = "Hello, World!"
    ciphertext = encrypt_message(plain_text, derived_key)
    decrypted_text = decrypt_message(ciphertext, derived_key)

    print(f"Decrypted text: {decrypted_text}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import logging
        logging.error(str(e))
