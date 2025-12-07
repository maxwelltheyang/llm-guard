import hashlib
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import os
import sqlite3
import secrets
from logging import getLogger, ERROR
from passlib.pwd import PasswordPolicy

logger = getLogger(__name__)
logger.setLevel(ERROR)

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

    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        hashed_password = hash_password(password)

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        logger.info(f"Password stored for user: {username}")
    except sqlite3.Error as e:
        logger.error(f"Error storing password: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def retrieve_user_password_hash(username):
    db_name = os.environ.get('DB_NAME', 'passwords.db')

    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        c.execute("SELECT password FROM users WHERE username=?", (username,))

        result = c.fetchone()

        if result:
            return result[0]
        else:
            logger.warning(f"No user found with name: {username}")
    except sqlite3.Error as e:
        logger.error(f"Error retrieving password hash: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def verify_login(username, provided_password):
    db_name = os.environ.get('DB_NAME', 'passwords.db')

    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))

        result = c.fetchone()

        if result:
            hashed_password = retrieve_user_password_hash(username)

            try:
                return pwd_context.verify(provided_password, hashed_password)
            except ValueError as e:
                logger.error(f"Invalid stored hash: {e}")
                return False

        conn.close()
        logger.warning(f"No user found with name: {username}")
    except sqlite3.Error as e:
        logger.error(f"Error retrieving password hash: {e}")

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

password = secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=')
print(f"Generated password: {password}")

# Testing the function
create_user("test_user", password)

is_valid = verify_login("test_user", password)
print(f"Password valid: {is_valid}")
