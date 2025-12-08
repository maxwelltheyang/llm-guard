import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt(plain_text, password):
    salt = get_random_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode())
    return salt + nonce + ciphertext + tag

def decrypt(encrypted_data, password):
    salt = encrypted_data[:16]
    nonce = encrypted_data[16:32]
    ciphertext = encrypted_data[32:-16]
    tag = encrypted_data[-16:]
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    try:
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.decode()
    except ValueError:
        return None

# Example usage
password = "mysecretpassword"
plain_text = "Hello, world!"
encrypted_data = encrypt(plain_text, password)
decrypted_text = decrypt(encrypted_data, password)
print("Encrypted:", encrypted_data.hex())
print("Decrypted:", decrypted_text)
