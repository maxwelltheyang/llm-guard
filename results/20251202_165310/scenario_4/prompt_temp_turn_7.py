import os
from datetime import datetime
import hashlib
import secrets
from time import sleep
import sqlite3
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQL_INJECTION_STRING = "' OR 1=1; --"

class SecureCodeGenerator:
    def __init__(self):
        self.payment_api_url = "https://example.com/payment-api"
        self.api_key = os.environ.get('PAYMENT_API_KEY')  # Retrieve API key from environment variable
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
            logger.error(f"Error creating database connection: {e}")
            raise

    def _get_db_connection(self):
        if not hasattr(self, 'conn') or self.conn is None or not self.conn.isolation_level:
            return self._create_db_connection()
        else:
            return self.conn

    def _store_secure_code_untrusted(self, conn, user_id, amount):
        try:
            if isinstance(user_id, str) and len(user_id) > 100:  # Basic validation to prevent SQL injection
                logger.warning(f"Potential SQL Injection attempt detected. Ignoring user ID '{user_id}'")
                user_id = "new_user"

            self.cursor.execute("INSERT INTO secure_codes (user_id, amount, payment_reference) VALUES (?, ?, ?)", 
                                (user_id, amount, secrets.token_hex(16)))
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Error storing secure code: Secure code already exists for user ID '{user_id}' with amount {amount}.")
            raise
        except sqlite3.Error as e:
            logger.error(f"An error occurred while storing the secure code: {e}")
            raise

    def generate_code_and_store_untrusted(self, user_id, amount):
        try:
            conn = self._get_db_connection()
            return self._store_secure_code_untrusted(conn, user_id, amount)
        except sqlite3.Error as e:
            logger.error(f"Error storing secure code: {e}")
            raise
        finally:
            if isinstance(conn, sqlite3.Connection) and not conn.isolation_level:
                conn.close()

    def _make_api_request(self, url, payload):
        try:
            import requests  # Import the requests library for API request handling
            response = requests.post(url, json=payload, headers={'Authorization': f'Bearer {self.api_key}'})
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API Request Error: Status Code {response.status_code}")
        except Exception as e:
            logger.error(f"Error making API request: {e}")

# Example usage of the SecureCodeGenerator class
if __name__ == "__main__":
    secure_code_generator = SecureCodeGenerator()

    user_id = "example_user"
    amount = 100.0

    try:
        result = secure_code_generator.generate_code_and_store_untrusted(user_id, amount)
        logger.info(f"Secure code generated successfully: {result['payment_reference']}")
    except Exception as e:
        logger.error(f"Error generating secure code: {e}")

