import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import os
import sqlite3
import secrets
from logging import getLogger, ERROR
from password_strength import PasswordStats

logger = getLogger(__name__)
logger.setLevel(ERROR)

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], default='pbkdf2_sha256')

# Define a single salt that will be used for all users
salt = hashlib.sha256(os.urandom(60)).digest()

def hash_password(password):
    # Use PBKDF2 with the defined salt to generate a password hash
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    return pwd_context.hash(password, salt=kdf)

def store_user_password(username, password):
    db_name = os.environ.get('DB_NAME', 'passwords.db')

    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        hashed_password = hash_password(password)

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        logger.info(f"Password stored for user: {username}")
    except sqlite3.Error as e:
        logger.error(f"Error storing password: {e}")
        try:
            if 'conn' in locals() and conn is not None:
                conn.close()
        except sqlite3.OperationalError:
            pass
    finally:
        if 'conn' in locals() and conn is not None:
            try:
                conn.close()
            except sqlite3.OperationalError:
                pass

def retrieve_user_password_hash(username):
    db_name = os.environ.get('DB_NAME', 'passwords.db')

    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        c.execute("SELECT password FROM users WHERE username=?", (username,))

        result = c.fetchone()

        if result is not None:
            return pwd_context.hash(result[0], salt=salt)

        logger.error(f"Error retrieving password for user: {username}")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

    try:
        conn.close()
    except sqlite3.OperationalError:
        pass

def generate_password():
    # Ensure the generated password has at least 8 characters and includes numbers, letters (both uppercase and lowercase), and special characters
    while True:
        password = secrets.token_urlsafe(32)

        stats = PasswordStats(password)

        if len(stats.common) > 4 or stats.repeat >= 3 \
                or (len(set(password)) - len(re.findall(r'[a-z]', password))) == 0 \
                or (len(set(password)) - len(re.findall(r'[A-Z]', password))) < 1 \
                or (len(set(password)) - len(re.findall(r'\d', password))) < 2 \
                or (len(set(password)) - len(re.findall(r'[^a-zA-Z\d\s]', password))) < 3:
            continue

        return password

password = generate_password()

# Testing the function
store_user_password("test_user", password)

is_valid = verify_login("test_user", password)
print(f"Password valid: {is_valid}")
