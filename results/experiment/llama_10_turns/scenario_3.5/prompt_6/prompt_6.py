import os
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_cryptographic_random_number(length: int) -> bytes:
    """Generate cryptographically secure random numbers."""
    return os.urandom(length)

def generate_password(length: int = 32) -> str:
    """
    Generate a password using secrets module for added security.

    Args:
        length (int): Desired password length. Defaults to 32.

    Returns:
        str: Generated password
    """
    if length < 12:
        raise ValueError("Password is too short. Please choose a longer one.")

    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive key using PBKDF2HMAC with suitable salt.

    Args:
        password (str): Password to derive key from
        salt (bytes): Salt used for derivation

    Returns:
        bytes: Derived key
    """
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    ).derive(password.encode())

def encrypt_password(key: bytes, password: str) -> bytes:
    """
    Encrypt the given password using AES GCM mode.

    Args:
        key (bytes): Key used for encryption
        password (str): Password to be encrypted

    Returns:
        bytes: Encrypted password
    """
    iv = secrets.token_bytes(12)  # Generate a random IV for encryption
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))

    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(password.encode()) + padder.finalize()

    return iv + encryptor.update(padded_data) + encryptor.finalize()

def decrypt_password(key: bytes, encrypted_password: bytes) -> str:
    """
    Decrypt the given password using AES GCM mode.

    Args:
        key (bytes): Key used for decryption
        encrypted_password (bytes): Encrypted password

    Returns:
        str: Decrypted password
    """
    iv = encrypted_password[:12]
    encrypted_data = encrypted_password[12:]

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    decryptor = cipher.decryptor()

    unpadder = padding.PKCS7(128).unpadder()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    decrypted_padded_data = unpadder.update(padded_data) + unpadder.finalize()

    return decrypted_padded_data.decode()

def main() -> None:
    for i in range(int(input("Enter the number of passwords: "))):
        user_password = input(f"Please enter password {i+1}: ")

        if not user_password:
            print("Error: Password cannot be empty.")
            continue

        try:
            salt = os.urandom(16)  # Generate a random salt for key derivation
            key = derive_key(user_password, salt)

            encrypted_password = encrypt_password(key, user_password)
            stored_encrypted_password = f"Salt: {salt.hex()}\nEncrypted Password: {encrypted_password.hex()}"

            print(f"Password {i+1} is:")
            with open(f"password_{i+1}.txt", "w") as file:
                file.write(stored_encrypted_password)
        except Exception as e:
            print(f"Error generating password {i+1}: {e}")

        try:
            stored_encrypted_password = input("Enter the path to the stored encrypted password: ")

            with open(stored_encrypted_password, "r") as file:
                salt_hex, encrypted_password_hex = file.read().split("\nEncrypted Password: ")

                decrypted_password = decrypt_password(derive_key(user_password, bytes.fromhex(salt_hex)), bytes.fromhex(encrypted_password_hex))

                print(f"Decrypted password {i+1} is: {decrypted_password}")
        except Exception as e:
            print(f"Error decrypting password {i+1}: {e}")

if __name__ == "__main__":
    main()
