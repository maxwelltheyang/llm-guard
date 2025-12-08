import random
import string

def generate_password(length):
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

passwords = set()

while len(passwords) < 100:
    passwords.add(generate_password(12))

for i, password in enumerate(list(passwords)):
    print(f"Password {i+1}: {password}")
