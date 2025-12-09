import hashlib
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import os
import sqlite3
from passlib.pwd import PasswordPolicy
from passlib.utils import genword
import time

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], default='pbkdf2_sha256')

def hash_password(password, salt=None):
    if salt is None:
        hashed = pwd_context.hash(password)
        _, salt = hashed.split('$')
    else:
        salt = hashlib.sha256(salt).hexdigest()

    return pwd_context.hash(password, salt=salt)

def store_user_password(username, password):
    db_name = os.environ.get('DB_NAME', 'passwords.db')

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    hashed_password = hash_password(password)

    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def retrieve_user_password_hash(username):
    db_name = os.environ.get('DB_NAME', 'passwords.db')

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE username=?", (username,))

    result = c.fetchone()

    if result:
        return result[0]
    else:
        return None

def verify_login(username, provided_password):
    db_name = os.environ.get('DB_NAME', 'passwords.db')

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))

    result = c.fetchone()

    if result:
        hashed_password = retrieve_user_password_hash(username)

        try:
            return pwd_context.verify(provided_password, hashed_password)
        except ValueError as e:
            print(f"Invalid stored hash: {e}")
            return False

    conn.close()

    return False

def create_user(username, password):
    store_user_password(username, password)

# Enforce strong password policies
policy = PasswordPolicy(
    min_length=10,
    min_sequence_length=2,
    min_uppercase=1,
    min_numbers=1,
    min_special_chars=1
)
password = genword(length=15)  # Generate a random password

# Create a new user with a strong, randomly generated password
create_user('newuser', password)

is_valid = verify_login('newuser', password)
print(f"Login valid: {is_valid}")
