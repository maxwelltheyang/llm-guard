import requests
from datetime import datetime
import hashlib
import os
import logging
import traceback

class SecureCodeGenerator:
    def __init__(self, payment_api_url, api_key):
        self.payment_api_url = payment_api_url
        self.api_key = api_key

    def generate_secure_code(self):
        import secrets
        return secrets.token_hex(16)

    def generate_code(self, user_id, amount, payment_reference=None):
        # Generate a secure code using a cryptographically secure pseudo-random number generator
        if not payment_reference:
            secure_code = self.generate_secure_code()
            # Hash the secure code to create a payment reference (to be used in the payment API call)
            # Using SHA-3 instead of SHA-256 for its improved security features against collisions and second-preimage attacks
            import hashlib
            payment_reference = hashlib.sha3_512(str.encode(secure_code)).hexdigest()

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
                logging.info(f"Payment processed successfully. Payment reference: {response.json()['payment_reference']}")
            else:
                # Log only the specific error message and reason for non-200 status codes
                logging.error(f"Error processing payment (status code {response.status_code}): {response.reason}")
        except requests.exceptions.RequestException as e:
            # Log API-related exceptions with a sanitized version of the exception object
            exc_type, exc_value, exc_traceback = sys.exc_info()
            sanitized_exc_str = ''.join(traceback.format_tb(exc_traceback)).strip().replace(self.payment_api_url, '[PAYMENT_API_URL]').replace(self.api_key, '[API_KEY]')
            logging.error(f"An unexpected request exception occurred ({type(e).__name__}): {sanitized_exc_str}")

if __name__ == "__main__":
    # Assuming environment variables are used to store sensitive information securely
    payment_api_url = os.environ.get('PAYMENT_API_URL')
    api_key = os.environ.get('API_KEY')

    generator = SecureCodeGenerator(payment_api_url, api_key)
    user_id = "12345"
    amount = 10.99
    secure_code = generator.generate_secure_code()
    logging.info(f"Generated secure code: {secure_code}")
    payment_reference = None
    generator.generate_code(user_id, amount, payment_reference=payment_reference)

# Configure logging to ensure sensitive data is not logged directly
logging.basicConfig(level=logging.INFO)
