from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

def encrypt(data, key):
    key = key[:32].ljust(32, b'\0')  # Ensure key is 32 bytes long
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    return cipher.iv + ct_bytes

def decrypt(ciphertext, key):
    key = key[:32].ljust(32, b'\0')  # Ensure key is 32 bytes long
    iv = ciphertext[:AES.block_size]
    ct = ciphertext[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size)

# Example usage:
key = os.urandom(32)
data = b'This is some data to encrypt'
encrypted = encrypt(data, key)
decrypted = decrypt(encrypted, key)
