from Crypto.Cipher import AES
import os

def encrypt_aes(key, data):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + ciphertext, tag

def decrypt_aes(key, encrypted_data, tag):
    cipher = AES.new(key, AES.MODE_EAX, nonce=encrypted_data[:16])
    try:
        plaintext = cipher.decrypt(encrypted_data[16:])
        cipher.verify(tag)
        return plaintext
    except (ValueError, KeyError):
        return None

# Example usage
key = os.urandom(16)  # AES-128
data = b'This is a secret message!'
encrypted_data, tag = encrypt_aes(key, data)
decrypted_data = decrypt_aes(key, encrypted_data, tag)

print("Original:", data)
print("Decrypted:", decrypted_data.decode() if decrypted_data else "Failed to decrypt")
