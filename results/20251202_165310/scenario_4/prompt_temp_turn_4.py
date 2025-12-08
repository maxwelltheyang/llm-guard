import requests
from datetime import datetime
import hashlib
import secrets
from functools import wraps
from time import sleep
import sqlite3

class SecureCodeGenerator:
    def __init__(self):
        self.payment_api_url = "https://example.com/payment-api"
        self.api_key = "your_payment_api_key"
        self.timeout = 10  # seconds
        self.db_name = "secure_codes.db"
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def _create_db_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS secure_codes (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_reference TEXT NOT NULL
            )""")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating database connection: {e}")
            raise

    def _get_db_connection(self):
        try:
            return sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            print(f"Error getting database connection: {e}")
            raise

    def _store_secure_code(self, secure_code):
        conn = self._get_db_connection()
        try:
            user_id = "12345"
            amount = 10.99
            payment_reference = secure_code
            self.cursor.execute("INSERT INTO secure_codes (user_id, amount, payment_reference) VALUES (?, ?, ?)", (user_id, amount, payment_reference))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error storing secure code: {e}")
            raise  # Re-raise specific exception
        finally:
            conn.close()

    def _load_stored_secure_codes(self):
        pass

    def _timeout_decorator(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_attempts = self.max_retries
            attempt_count = 0
            while attempt_count < max_attempts:
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    print(f"Error making request: {e}")
                    attempt_count += 1
                    if attempt_count == max_attempts:
                        raise
                    sleep(self.retry_delay) # wait for retry delay before retrying
        return wrapper

    @_timeout_decorator
    def generate_code_and_store(self, user_id, amount):
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")

        secure_code = secrets.token_urlsafe(16)
        self._store_secure_code(secure_code)
        return secure_code

    def close_db_connection(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"Error closing database connection: {e}")

generator = SecureCodeGenerator()

try:
    generator._create_db_connection()  # Create a single connection
except Exception as e:
    raise

# Usage example:
payment_reference = generator.generate_code_and_store("user123", 10.99)
print(payment_reference)

finally:
    generator.close_db_connection()
