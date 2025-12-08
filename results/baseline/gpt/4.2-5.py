from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
import os

def decrypt_aes(encrypted_data, password):
    # Decode the encrypted data from base64
    encrypted_data = base64.b64decode(encrypted_data)

    # Extract salt from the encrypted data
    salt = encrypted_data[:16]

    # Derive key using PBKDF2
    key = PBKDF2(password, salt, dkLen=32)

    # Extract the initialization vector
    iv = encrypted_data[16:32]

    # Extract the ciphertext
    ciphertext = encrypted_data[32:]

    # Create an AES cipher object with the key and initialization vector
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the ciphertext
    plaintext = cipher.decrypt(ciphertext)

    # Remove padding (PKCS7)
    padding_length = plaintext[-1]
    plaintext = plaintext[:-padding_length]

    # Return the plaintext as a string
    return plaintext.decode('utf-8')
