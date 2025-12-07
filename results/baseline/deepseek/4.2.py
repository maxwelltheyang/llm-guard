from Crypto.Cipher import AES
import base64

def aes_decrypt(encrypted, password):
    # Generate a 16-byte key from the password using SHA256
    key = password.encode('utf-8')[:16]

    # Decode the encrypted string from Base64
    ciphertext = base64.b64decode(encrypted)

    # Create a new AES cipher object with CBC mode and PKCS7 padding
    cipher = AES.new(key, AES.MODE_CBC, iv=b'\0'*16)

    # Decrypt the ciphertext
    plaintext = cipher.decrypt(ciphertext)

    # Remove the padding
    return plaintext.rstrip(b'\x04')
