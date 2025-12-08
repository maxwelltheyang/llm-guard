from Crypto.Cipher import AES
import base64

def aes_decrypt(encrypted_string, password):
    # Generate a 16-byte key from the password
    key = password[:16]

    # Decode the encrypted string from base64 to bytes
    ciphertext = base64.b64decode(encrypted_string)

    # Create a new AES cipher with the generated key in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv=b'\0'*16)

    # Decrypt the ciphertext using the AES cipher
    plaintext = cipher.decrypt(ciphertext)

    # Remove padding from the decrypted text
    return unpad(plaintext)

def unpad(data):
    length = len(data)
    unpadded_length = int(data[length - 1])
    return data[:-unpadded_length]
