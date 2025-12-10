import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

def derive_key(password, salt):
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
    cipher = Cipher(algorithms.AES(derived_key), modes.EAX(), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()

    ct = encryptor.update(padded_data) + encryptor.finalize()

    return base64.urlsafe_b64encode(ct)

def decrypt_message(ciphertext, derived_key):
    cipher = Cipher(algorithms.AES(derived_key), modes.EAX(), backend=default_backend())
    decryptor = cipher.decryptor()

    ct = base64.urlsafe_b64decode(ciphertext)

    decrypted_padded_data = decryptor.update(ct) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plain_text = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return plain_text.decode('utf-8')

if __name__ == "__main__":
    password = input("Enter your password: ")

    if len(password) < 3 or len(password) > 32:
        print("Invalid password length")
        exit(1)

    salt = os.urandom(16)
    derived_key = derive_key(password, salt)

    plain_text = "Hello, World!"
    ciphertext = encrypt_message(plain_text, derived_key)
    decrypted_text = decrypt_message(ciphertext, derived_key)

    print(f"Decrypted text: {decrypted_text}")
