from flask import Flask, request, jsonify
from twilio.rest import Client
import os
import secrets

app = Flask(__name__)

# Environment variable configuration
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
app.config['DEBUG'] = FLASK_DEBUG

# Configuration for Twilio and Email using environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
if not TWILIO_ACCOUNT_SID:
    raise ValueError("TWILIO_ACCOUNT_SID is not set")

TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
if not TWILIO_AUTH_TOKEN:
    raise ValueError("TWILIO_AUTH_TOKEN is not set")

TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
if not TWILIO_PHONE_NUMBER:
    raise ValueError("TWILIO_PHONE_NUMBER is not set")

EMAIL_SENDER = os.getenv('EMAIL_SENDER')
if not EMAIL_SENDER:
    raise ValueError("EMAIL_SENDER is not set")

EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
if not EMAIL_PASSWORD:
    raise ValueError("EMAIL_PASSWORD is not set")

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def generate_otp():
    return secrets.randbits(16)  # Generate a 16-bit random number

def send_otp(recipient):
    otp = generate_otp()
    message = twilio_client.messages.create(
        to=recipient,
        from_=TWILIO_PHONE_NUMBER,
        body=f"Your OTP is: {otp}"
    )
    return otp

@app.route('/send-otp', methods=['POST'])
def send_otp_endpoint():
    data = request.get_json()
    recipient = data.get('recipient')
    if not recipient:
        return jsonify({"error": "Recipient is required"}), 400

    otp = send_otp(recipient)
    return jsonify({"message": f"OTP sent to {recipient}. Your OTP is: {otp}"})

if __name__ == '__main__':
    app.run()
