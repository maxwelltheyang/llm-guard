from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def encrypt_aes(plaintext):
    key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)   # 128-bit IV

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    ct = encryptor.update(padded_data) + encryptor.finalize()

    return key, iv, ct

def decrypt_aes(key, iv, ct):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    decryptor = cipher.decryptor()

    pt = decryptor.update(ct) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    pt = unpadder.update(pt) + unpadder.finalize()

    return pt

plaintext = b"This is some secret data"
key, iv, ct = encrypt_aes(plaintext)
print(f"Encrypted text: {ct.hex()}")
pt = decrypt_aes(key, iv, ct)
print(f"Decrypted text: {pt.decode()}")
