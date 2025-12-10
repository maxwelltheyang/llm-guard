import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import secrets

def derive_key(password, salt):
    """
    Derives a key from the user-provided password and salt using PBKDF2.

    Args:
        password (str): The user-provided password.
        salt (bytes): A random salt value used in the derivation process.

    Returns:
        bytes: The derived key.
    """
    # Use secrets to generate a cryptographically secure pseudo-random number for the salt
    salt = secrets.token_bytes(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=3000000,
        backend=default_backend()
    )

    derived_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return derived_key

def encrypt_message(plain_text, derived_key):
    """
    Encrypts the given plain text using AES in EAX mode.

    Args:
        plain_text (str): The plaintext to be encrypted.
        derived_key (bytes): The key used for encryption.

    Returns:
        bytes: The ciphertext.
    """
    cipher = Cipher(algorithms.AES(derived_key), modes.EAX(), backend=default_backend())
    encryptor = cipher.encryptor()

    # Convert the plain text to bytes
    plain_text_bytes = plain_text.encode('utf-8')

    # Pad the plaintext
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text_bytes) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext

def decrypt_message(ciphertext, derived_key):
    """
    Decrypts the given ciphertext using AES in EAX mode.

    Args:
        ciphertext (bytes): The encrypted message to be decrypted.
        derived_key (bytes): The key used for decryption.

    Returns:
        str: The decrypted text.
    """
    cipher = Cipher(algorithms.AES(derived_key), modes.EAX(), backend=default_backend())
    decryptor = cipher.decryptor()

    ciphertext_bytes = base64.urlsafe_b64decode(ciphertext)
    padded_data = decryptor.update(ciphertext_bytes) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plain_text_bytes = unpadder.update(padded_data) + unpadder.finalize()

    # Convert the bytes to a string
    plain_text = plain_text_bytes.decode('utf-8')

    return plain_text

def main():
    password = input("Enter your password: ")

    if len(password) < 8:
        print("Invalid password length. Please use a password at least 8 characters long.")
        exit(1)

    salt = secrets.token_bytes(16)
    derived_key = derive_key(password, salt)

    plain_text = "Hello, World!"
    ciphertext = encrypt_message(plain_text, derived_key)
    decrypted_text = decrypt_message(ciphertext, derived_key)

    print(f"Decrypted text: {decrypted_text}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
