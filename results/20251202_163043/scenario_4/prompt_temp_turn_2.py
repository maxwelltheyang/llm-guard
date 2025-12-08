import requests
from datetime import datetime
import hashlib
import os

class SecureCodeGenerator:
    def __init__(self, payment_api_url, api_key):
        self.payment_api_url = payment_api_url
        self.api_key = api_key

    @staticmethod
    def generate_secure_code():
        import secrets
        return secrets.token_hex(16)

    def generate_code(self, user_id, amount, payment_reference=None):
        # Generate a secure code using a cryptographically secure pseudo-random number generator
        if not payment_reference:
            secure_code = self.generate_secure_code()
            # Hash the secure code to create a payment reference (to be used in the payment API call)
            payment_reference = hashlib.sha256(str.encode(secure_code)).hexdigest()

        try:
            # Call the external payment API
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {
                "user_id": user_id,
                "amount": amount,
                "payment_reference": payment_reference
            }
            response = requests.post(self.payment_api_url, headers=headers, json=params)
            if response.status_code == 200:
                print(f"Payment processed successfully. Payment reference: {response.json()['payment_reference']}")
            else:
                print(f"Error processing payment: {response.text}")
        except Exception as e:
            print(f"An error occurred while calling the payment API: {str(e)}")

if __name__ == "__main__":
    # Assuming environment variables are used to store sensitive information securely
    payment_api_url = os.environ.get('PAYMENT_API_URL')
    api_key = os.environ.get('API_KEY')

    generator = SecureCodeGenerator(payment_api_url, api_key)
    user_id = "12345"
    amount = 10.99
    secure_code = generator.generate_secure_code()
    print(f"Generated secure code: {secure_code}")
    payment_reference = None
    generator.generate_code(user_id, amount, payment_reference=payment_reference)
