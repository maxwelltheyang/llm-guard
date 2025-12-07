import requests
from datetime import datetime
import hashlib

class SecureCodeGenerator:
    def __init__(self):
        self.payment_api_url = "https://example.com/payment-api"
        self.api_key = "your_payment_api_key"

    def generate_code(self, user_id, amount):
        # Step 1: Generate a secure code using a cryptographically secure pseudo-random number generator
        import secrets
        secure_code = secrets.token_hex(16)

        # Step 2: Hash the secure code to create a payment reference (to be used in the payment API call)
        payment_reference = hashlib.sha256(str.encode(secure_code)).hexdigest()

        try:
            # Step 3: Call the external payment API
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

    def verify_code(self, secure_code):
        # For demonstration purposes only (not recommended to store secure codes in plain text)
        if self.generate_secure_code() == secure_code:
            return True
        else:
            return False

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
