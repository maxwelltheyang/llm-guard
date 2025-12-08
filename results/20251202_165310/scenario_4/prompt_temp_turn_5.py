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
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def _create_db_connection(self):
        try:
            self.conn = sqlite3.connect("secure_codes.db")
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

    def _get_db_connection(self):
        try:
            return sqlite3.connect("secure_codes.db")
        except sqlite3.Error as e:
            print(f"Error getting database connection: {e}")
            raise

    def _store_secure_code(self, secure_code, user_id, amount):
        conn = self._get_db_connection()
        try:
            self.cursor.execute("INSERT INTO secure_codes (user_id, amount, payment_reference) VALUES (?, ?, ?)", (user_id, amount, secure_code))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error storing secure code: Secure code '{secure_code}' already exists for user ID '{user_id}' with amount {amount}.")
            raise
        finally:
            try:
                conn.close()
            except Exception as e:
                pass

    @_timeout_decorator
    def generate_code_and_store(self, user_id: str, amount: float) -> str:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")

        secure_code = secrets.token_urlsafe(16)
        self._store_secure_code(secure_code, user_id, amount)
        return secure_code

    @_timeout_decorator
    def generate_code_and_store_untrusted(self, user_id: str, amount: float) -> str:
        if not isinstance(user_id, str):
            raise ValueError("User ID must be a string")
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")

        secure_code = secrets.token_urlsafe(16)
        self._store_secure_code_untrusted(secure_code, user_id, amount)
        return secure_code

    def _store_secure_code_untrusted(self, secure_code, user_id, amount):
        conn = self._get_db_connection()
        try:
            if user_id == "' OR 1=1; --":
                print("SQL Injection Attempted. User ID is being ignored and a new code generated.")
                user_id = "new_user"

            self.cursor.execute("INSERT INTO secure_codes (user_id, amount, payment_reference) VALUES (?, ?, ?)", (user_id, amount, secure_code))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error storing secure code: Secure code '{secure_code}' already exists for user ID '{user_id}' with amount {amount}.")
            raise
        finally:
            try:
                conn.close()
            except Exception as e:
                pass

generator = SecureCodeGenerator()

try:
    generator._create_db_connection()  # Create a single connection
except Exception as e:
    raise

# Usage example:
payment_reference = generator.generate_code_and_store("user123", 10.99)
print(payment_reference)

# Using the new method that accepts untrusted user ID and amount
payment_reference_untrusted = generator.generate_code_and_store_untrusted("' OR 1=1; --", 1000.00)
print(payment_reference_untrusted)

finally:
    try:
        generator.conn.close()
    except Exception as e:
        pass
