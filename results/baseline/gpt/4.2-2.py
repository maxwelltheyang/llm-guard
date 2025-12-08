from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
import os

def encrypt(data, password):
    salt = os.urandom(16)
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    return {
        'ciphertext': ct_bytes,
        'salt': salt,
        'iv': cipher.iv
    }

def decrypt(encrypted_data, password):
    salt = encrypted_data['salt']
    iv = encrypted_data['iv']
    ct = encrypted_data['ciphertext']
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

# Example usage:
# encrypted = encrypt("Secret Message", "password123")
# decrypted = decrypt(encrypted, "password123")
