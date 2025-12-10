import hashlib
import secrets
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import logging
import os
from typing import Tuple

logging.basicConfig(level=logging.INFO)

class KeyDeriver:
    def __init__(self):
        self.iterations = 524288

    def derive_key(self, password_bytes: bytes, salt: bytes) -> bytes:
        try:
            kdf = hashlib.pbkdf2_hmac('sha512', password_bytes, salt, self.iterations, 32)
            return kdf
        except Exception as e:
            logging.error("Key derivation failed: %s", e)
            raise

class AESCipher:
    def __init__(self, key: bytes):
        self.aes = algorithms.AES(key)

    def encrypt(self, message: bytes) -> bytes:
        if not isinstance(message, bytes) or len(message) == 0:
            raise ValueError("Message cannot be empty.")

        try:
            iv = secrets.token_bytes(12)
            cipher = Cipher(self.aes, modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()

            padded_data = padder.update(message) + padder.finalize()
            ct = encryptor.update(padded_data) + encryptor.finalize()
            return iv + ct
        except Exception as e:
            logging.error("Encryption failed: %s", e)
            raise

    def decrypt(self, encrypted_message: bytes) -> bytes:
        try:
            iv = encrypted_message[:12]
            ct = encrypted_message[12:]
            cipher = Cipher(self.aes, modes.GCM(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            pt = decryptor.update(ct) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()

            return unpadder.update(pt) + unpadder.finalize()
        except Exception as e:
            logging.error("Decryption failed: %s", e)
            raise

class SecureEncryptor:
    def __init__(self):
        self.key_deriver = KeyDeriver()

    def generate_key_and_iv(self, password: str) -> Tuple[bytes, bytes]:
        salt = secrets.token_bytes(16)
        key = self.key_deriver.derive_key(password.encode(), salt)
        iv = secrets.token_bytes(12)
        return key, iv

    def encrypt(self, message: bytes, key: bytes) -> bytes:
        aes_cipher = AESCipher(key)
        return aes_cipher.encrypt(message)

    def decrypt(self, encrypted_message: bytes, key: bytes) -> bytes:
        aes_cipher = AESCipher(key)
        return aes_cipher.decrypt(encrypted_message)

def main():
    secure_encryptor = SecureEncryptor()

    password = "secure_password"
    key, iv = secure_encryptor.generate_key_and_iv(password)
    logging.info("Key: %s", key.hex())
    logging.info("IV: %s", iv.hex())

    message = "Hello, World!".encode()

    encrypted_message = secure_encryptor.encrypt(message, key)
    logging.info("Encrypted message: %s", encrypted_message.hex())

    decrypted_message = secure_encryptor.decrypt(encrypted_message, key)
    if decrypted_message is not None:
        logging.info("Decrypted message: %s", decrypted_message.decode())
    else:
        logging.error("Failed to decrypt the message.")

if __name__ == "__main__":
    main()
