import hashlib
from cryptography.fernet import Fernet
from passlib.context import CryptContext
import os
import sqlite3
import secrets
from logging import getLogger, ERROR
from password_strength import PasswordStats
import uuid

logger = getLogger(__name__)
logger.setLevel(ERROR)

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], default='pbkdf2_sha256')

def hash_password(password):
    salt = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
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

        if result:
            return result[0]
        else:
            logger.warning(f"No user found with name: {username}")
    except sqlite3.Error as e:
        logger.error(f"Error retrieving password hash: {e}")
    finally:
        try:
            if 'conn' in locals() and conn is not None:
                conn.close()
        except sqlite3.OperationalError:
            pass

def generate_password():
    # Define strong password policies
    policy = PasswordStats(policy)

    while True:
        password = secrets.token_urlsafe(16)  # Generate a random URL-safe string

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
