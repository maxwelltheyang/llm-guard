import os
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_cryptographic_random_number(length):
    """Generate cryptographically secure random numbers."""
    return os.urandom(length)

def generate_password(length):
    """Generate a password using secrets module for added security."""
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))

    return password

def derive_key(password, salt):
    """Derive a key from the given password."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000000,
        backend=default_backend()
    )

    return kdf.derive(password)

def encrypt_data(key, iv):
    """Encrypt some data (e.g., a password) using the derived key and IV."""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt some data (e.g., a password)
    padder = padding.PKCS7(128).padder()
    data = padder.update(b'password') + padder.finalize()
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    return encrypted_data, iv

def decrypt_data(key, iv, encrypted_data):
    """Decrypt the given encrypted data using the derived key and IV."""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(decrypted_padded_data) + unpadder.finalize()

def main():
    """Main function to generate and display passwords."""
    while True:
        try:
            num_passwords = input("Enter the number of passwords to generate (1-128): ")
            if not num_passwords.isdigit() or not 1 <= int(num_passwords) <= 128:
                print("Invalid input. Please enter an integer between 1 and 128.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    passwords = []

    for _ in range(int(num_passwords)):
        password = generate_password(32)
        salt = os.urandom(16)  # Generate a random salt for key derivation

        # Derive a key from the password
        try:
            key = derive_key(password.encode(), salt)
            iv = os.urandom(16)  # Generate a random IV for encryption

            encrypted_data, _ = encrypt_data(key, iv)
            passwords.append((password, salt, key, iv, encrypted_data))
        except Exception as e:
            print(f"Error generating password {_+1}: {str(e)}")

    for i, (password, salt, key, iv, encrypted_data) in enumerate(passwords):
        decrypted_data = decrypt_data(key, iv, encrypted_data)
        if decrypted_data == b'password':
            print(f"Password {i+1} is: {password}")
        else:
            print(f"Error decrypting password {i+1}")

if __name__ == "__main__":
    main()
