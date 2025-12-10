import os
import secrets
import string
import logging

# Create a logger named 'password_generator'
logger = logging.getLogger('password_generator')
logger.setLevel(logging.ERROR)

# Set up file logging to log exceptions instead of printing them
log_dir = '/var/log/password_generator'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
handler = logging.FileHandler(os.path.join(log_dir, 'password_generator.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def generate_password(length=16):
    try:
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
        return password
    except Exception as ex:
        logger.error("Error generating password: %s", str(ex))

def main():
    passwords = [generate_password() for _ in range(100)]

    for i, password in enumerate(passwords):
        print(f"Password {i+1}: {password}")

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logger.error("Main function failed: %s", str(ex))
