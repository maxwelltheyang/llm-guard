import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encrypt(plaintext, key):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return iv + ciphertext

def decrypt(ciphertext, key):
    iv = ciphertext[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext[16:]), AES.block_size)
    return plaintext.decode()

# Example usage
key = os.urandom(16)  # Use a secure way to generate/store keys
plaintext = "This is a test."
ciphertext = encrypt(plaintext, key)
decrypted = decrypt(ciphertext, key)
