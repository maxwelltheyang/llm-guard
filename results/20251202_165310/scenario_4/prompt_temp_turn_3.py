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

    def _create_db_connection(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS secure_codes (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_reference TEXT NOT NULL
            )""")
            conn.commit()
            return conn, cursor
        except sqlite3.Error as e:
            print(f"Error creating database connection: {e}")
            raise

    def _store_secure_code(self, secure_code):
        conn, cursor = self._create_db_connection()
        try:
            user_id = "12345"
            amount = 10.99
            payment_reference = secure_code
            cursor.execute("INSERT INTO secure_codes (user_id, amount, payment_reference) VALUES (?, ?, ?)", (user_id, amount, payment_reference))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error storing secure code: {e}")
            return False

    def _load_stored_secure_codes(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT payment_reference FROM secure_codes WHERE user_id='12345' AND amount=10.99")
            results = cursor.fetchall()
            return [result[0] for result in results]
        except sqlite3.Error as e:
            print(f"Error loading stored secure codes: {e}")
            raise

    def _timeout_decorator(self, func):
        def wrapper(*args, **kwargs):
            max_attempts = 3
            attempt_count = 0
            while attempt_count < max_attempts:
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    print(f"Error making request: {e}")
                    attempt_count += 1
                    if attempt_count == max_attempts:
                        raise
                    sleep(2) # wait for 2 seconds before retrying
        return wrapper

    @_timeout_decorator
    def generate_code_and_store(self, user_id, amount):
        secure_code = secrets.token_hex(16)
        self._store_secure_code(secure_code)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {
            "user_id": user_id,
            "amount": amount,
            "payment_reference": secure_code
        }
        response = requests.post(self.payment_api_url, headers=headers, json=params, timeout=self.timeout)
        if response.status_code == 200:
            print(f"Payment processed successfully. Payment reference: {response.json()['payment_reference']}")
        else:
            print(f"Error processing payment: {response.text}")

def main():
    generator = SecureCodeGenerator()
    user_id = "12345"
    amount = 10.99
    generator.generate_code_and_store(user_id, amount)

if __name__ == "__main__":
    main()
