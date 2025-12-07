from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

def encrypt(plaintext):
    key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)  # 128-bit IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()
    ct = encryptor.update(padded_data) + encryptor.finalize()

    return iv + ct

# Example usage:
plaintext = b"This is a secret message"
encrypted = encrypt(plaintext)
print(f"IV: {encrypted[:16]}")
print(f"Ciphertext: {encrypted[16:]}")
