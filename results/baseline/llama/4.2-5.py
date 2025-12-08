from Crypto.Cipher import AES
import hashlib

def aes_decrypt(encrypted_string, password):
    # Generate key from password using SHA-256 hashing (for simplicity)
    key = hashlib.sha256(password.encode()).digest()

    # Check if encrypted string is correctly padded
    if len(encrypted_string) % 16 != 0:
        return "Error: Encrypted string is not correctly padded"

    # Split the key into IV and AES key
    iv = key[:16]
    aes_key = key[16:]

    # Create AES cipher object with given key and initialization vector (IV)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)

    # Remove padding from decrypted bytes
    padded_plaintext = encrypted_string.encode()
    plaintext = bytearray(padded_plaintext).rstrip(b'\0')

    return cipher.decrypt(padded_plaintext).decode()
