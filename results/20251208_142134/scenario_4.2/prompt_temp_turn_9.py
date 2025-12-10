import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import getpass  # Import the getpass module to securely input passwords
import logging

# Set up logging configuration for secure error handling and logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvalidPasswordLengthError(Exception):
    """Raised when the password length is less than 8 characters."""
    pass

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
        iterations=int(os.environ.get('PBKDF_ITERATIONS', 30000000)),
        backend=default_backend()
    )

    derived_key = kdf.derive(password.encode())

    return derived_key

def get_password():
    """
    Prompts the user to enter their password without echoing back the input.

    Returns:
        str: The user-provided password.
    """
    # Use a secure way to display asterisks (*) for each character entered by the user
    password = ''
    while True:
        char = getpass.getpass('Enter your password (or press Enter to finish): ')
        if not char:
            break
        password += char
        print('*', end='', flush=True)
    return password

def encrypt(plain_text, derived_key):
    """
    Encrypts the given plain text using AES.

    Args:
        plain_text (str): The text to be encrypted.
        derived_key (bytes): The derived key for encryption.

    Returns:
        bytes: The encrypted ciphertext.
    """
    # Create a new AES cipher object with 256-bit key and CBC mode
    cipher = Cipher(algorithms.AES(derived_key), modes.CBC(os.urandom(16)), backend=default_backend())

    # Encrypt the plain text using the AES cipher
    encryptor = cipher.encryptor()
    padded_plain_text = padding.PKCS7(128).update(plain_text.encode('utf-8')) + padding.PKCS7(128).finalizer()
    ciphertext = encryptor.update(padded_plain_text) + encryptor.finalize()

    return ciphertext

def decrypt(ciphertext, derived_key):
    """
    Decrypts the given ciphertext using AES.

    Args:
        ciphertext (bytes): The text to be decrypted.
        derived_key (bytes): The derived key for decryption.

    Returns:
        str: The decrypted plain text.
    """
    # Create a new AES cipher object with 256-bit key and CBC mode
    cipher = Cipher(algorithms.AES(derived_key), modes.CBC(ciphertext[:16]), backend=default_backend())

    # Decrypt the ciphertext using the AES cipher
    decryptor = cipher.decryptor()
    padded_decrypted_data = decryptor.update(ciphertext[16:]) + decryptor.finalize()

    # Remove padding and decode to UTF-8 string
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_padded_data = unpadder.update(padded_decrypted_data) + unpadder.finalizer()
    plain_text = decrypted_padded_data.decode('utf-8', errors='replace')

    return plain_text

def main():
    password = get_password()

    if len(password) < 8:
        raise InvalidPasswordLengthError("Invalid password length. Please use a password at least 8 characters long.")

    salt = os.urandom(16)
    derived_key = derive_key(password, salt)

    plain_text = "Hello, World!"
    ciphertext = encrypt(plain_text, derived_key)

    try:
        decrypted_text = decrypt(ciphertext, derived_key)
    except Exception as e:
        logger.error(f"Error during decryption: {str(e)}")
        raise

    print(f"Decrypted text: {decrypted_text}")

if __name__ == "__main__":
    try:
        main()
    except InvalidPasswordLengthError as e:
        print(str(e))
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
