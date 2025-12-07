import hashlib

def encrypt(plain_text, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cipher_suite = AES.new(hashed_password[:32].encode(), AES.MODE_EAX)
    encrypted_data, tag = cipher_suite.encrypt_and_digest(plain_text.encode())
    return cipher_suite.nonce.hex() + tag.hex() + encrypted_data.hex()

def decrypt(cipher_text, password):
    parts = [bytes.fromhex(x) for x in cipher_text.split(':')]
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    nonce = bytes.fromhex(parts[0])
    tag = parts[1]
    encrypted_data = parts[2]
    cipher_suite = AES.new(hashed_password[:32].encode(), AES.MODE_EAX, nonce)
    return cipher_suite.decrypt_and_verify(encrypted_data, tag).decode()
