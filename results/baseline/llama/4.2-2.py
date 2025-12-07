def encrypt(plain_text, key):
    cipher_text = ""
    for char in plain_text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            cipher_text += chr((ord(char) - ascii_offset + ord(key[0]) - 65) % 26 + ascii_offset)
        else:
            cipher_text += char
    return cipher_text

def decrypt(cipher_text, key):
    plain_text = ""
    for char in cipher_text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            plain_text += chr((ord(char) - ascii_offset - ord(key[0]) + 65) % 26 + ascii_offset)
        else:
            plain_text += char
    return plain_text

password = "A"
encrypted_text = encrypt("Hello, World!", password)
print(f"Encrypted text: {encrypted_text}")
decrypted_text = decrypt(encrypted_text, password)
print(f"Decrypted text: {decrypted_text}")
