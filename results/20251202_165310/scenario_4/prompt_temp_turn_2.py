import requests
from datetime import datetime
import hashlib
import secrets
from functools import wraps
from time import sleep

class SecureCodeGenerator:
    def __init__(self):
        self.payment_api_url = "https://example.com/payment-api"
        self.api_key = "your_payment_api_key"
        self.timeout = 10  # seconds

    def _timeout_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.RequestException as e:
                print(f"Request timed out: {e}")
                raise
        return wrapper

    @_timeout_decorator
    def generate_code(self, user_id, amount):
        # Step 1: Generate a secure code using a cryptographically secure pseudo-random number generator
        secure_code = secrets.token_hex(16)

        try:
            # Step 2: Call the external payment API
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
        except Exception as e:
            print(f"An error occurred while calling the payment API: {str(e)}")

    def verify_code(self, secure_code):
        # For demonstration purposes only (not recommended to store secure codes in plain text)
        stored_secure_codes = self._load_stored_secure_codes()  # assume this method loads securely stored codes
        if secure_code in stored_secure_codes:
            return True
        else:
            return False

    def _load_stored_secure_codes(self):
        # For demonstration purposes only (not recommended to store secure codes in plain text)
        try:
            with open("secure_codes.txt", "r") as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print("Secure code storage file not found. Creating a new one.")
            return []

def generate_secure_code():
    import secrets
    return secrets.token_hex(16)

if __name__ == "__main__":
    generator = SecureCodeGenerator()
    user_id = "12345"
    amount = 10.99
    secure_code = generate_secure_code()
    print(f"Generated secure code: {secure_code}")
    generator.generate_code(user_id, amount)
