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
    """Generate a password using secrets module for added security."""
    if length < 12:
        raise ValueError("Password is too short. Please choose a longer one.")

    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive key from password using PBKDF2HMAC."""
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    ).derive(password.encode())

def encrypt_data(key: bytes, iv: bytes, data: str) -> tuple:
    """Encrypt data using AES in GCM mode."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()

    ct = encryptor.update(data.encode()) + encryptor.finalize()

    return ct, iv

def decrypt_data(key: bytes, iv: bytes, ct: bytes) -> str:
    """Decrypt data using AES in GCM mode."""
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    decryptor = cipher.decryptor(ct)

    pt = decryptor.finalize()

    return pt.decode()

def main():
    try:
        num_passwords = int(input("Enter the number of passwords to generate (1-128): "))

        if 1 <= num_passwords <= 128:
            pass
        else:
            raise ValueError("Please enter a valid integer between 1 and 128.")
    except ValueError as e:
        print(f"Invalid input: {e}")
        return

    for i in range(num_passwords):
        password_length = int(input(f"Enter desired password length (default: 32) or press Enter to use default, then new password: "))

        if password_length:
            password = generate_password(password_length)
        else:
            user_password = input("Please enter a new password: ")

            try:
                password = generate_password()

                if len(user_password) < 12:
                    print("Password is too short. Please choose a longer one.")
                    continue

                salt = os.urandom(16)  # Generate a random salt for key derivation
                key = derive_key(user_password, salt)

                iv = secrets.token_bytes(12)  # Generate a random IV for encryption
                ct, _ = encrypt_data(key, iv, password)

                print(f"Password {i+1} is: {password}")
            except ValueError as e:
                print(f"Error generating password {i+1}: {e}")

        try:
            salt = os.urandom(16)  # Generate a random salt for key derivation
            key = derive_key(password, salt)

            iv = secrets.token_bytes(12)  # Generate a random IV for encryption

            ct, _ = encrypt_data(key, iv, password)

            print(f"Encrypted password {i+1} is: {ct.hex()}")
        except Exception as e:
            print(f"Error generating encrypted password {i+1}: {e}")

        try:
            key = derive_key(password, salt)
            decrypted_password = decrypt_data(key, iv, ct.decode())

            print(f"Decrypted password {i+1} is: {decrypted_password}")
        except Exception as e:
            print(f"Error decrypting password {i+1}: {e}")

if __name__ == "__main__":
    main()
