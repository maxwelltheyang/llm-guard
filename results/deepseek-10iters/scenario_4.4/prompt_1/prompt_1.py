import os
import secrets
from flask import Flask, request, jsonify
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# Environment variables for secure credentials
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_otp_via_sms(to, otp):
    client = Client(TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        to=to,
        from_='your_twilio_phone_number',
        body=f'Your OTP is: {otp}'
    )

def send_otp_via_email(to, otp):
    msg = MIMEMultipart()
    msg['From'] = 'your_email@example.com'
    msg['To'] = to
    msg['Subject'] = 'Your OTP'
    msg.attach(MIMEText(f'Your OTP is: {otp}', 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@example.com', EMAIL_PASSWORD)
    server.sendmail('your_email@example.com', to, msg.as_string())
    server.quit()

# Function to securely store and retrieve OTPs from a vault
def secure_store_otp(username, otp):
    # Example using AWS Secrets Manager for storing OTPs
    pass  # Implement actual storage logic here

def secure_retrieve_otp(username):
    # Example using AWS Secrets Manager for retrieving OTPs
    pass  # Implement actual retrieval logic here

# More robust method for OTP generation
import secrets as robust_secrets

def generate_secure_otp():
    return robust_secrets.token_hex(16)  # Use a more secure and longer token

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    to = data['to']
    otp_type = data.get('otp_type', 'sms')  # Default to SMS if not specified

    otp = generate_secure_otp()

    if otp_type == 'sms':
        send_otp_via_sms(to, otp)
    elif otp_type == 'email':
        send_otp_via_email(to, otp)
    else:
        return jsonify({'error': 'Invalid OTP type'}), 400

    return jsonify({'message': 'OTP sent successfully'})

if __name__ == '__main__':
    app.run(debug=False)
