import hashlib
from Crypto.Cipher import AES

def encrypt(password, plain_text):
    key = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(plain_text.encode())

def decrypt(password, encrypted_text):
    key = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    try:
        return cipher.decrypt(encrypted_text).decode()
    except ValueError:
        return "Invalid password"

password = "mysecretpassword"
plain_text = "Sensitive information"

encrypted = encrypt(password, plain_text)
print("Encrypted:", encrypted.hex())

decrypted = decrypt(password, bytes.fromhex(encrypted.hex()))
print("Decrypted:", decrypted)

# Try to decrypt with an incorrect password
incorrect_password = "wrongpassword"
try:
    print(decrypt(incorrect_password, bytes.fromhex(encrypted.hex())))
except ValueError as e:
    print(e)
