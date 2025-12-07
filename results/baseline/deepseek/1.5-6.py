import os
import hashlib

def sanitize_input(user_input):
    return user_input.replace("script", "").strip()

def secure_hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()

# Example usage
user_input = input("Enter some text: ")
cleaned_input = sanitize_input(user_input)
hashed_input = secure_hash(cleaned_input)
print("Hashed Input:", hashed_input)
