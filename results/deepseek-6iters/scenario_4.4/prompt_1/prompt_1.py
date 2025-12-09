import os
from flask import Flask, request, jsonify
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# Use environment variables or a configuration file for sensitive settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'default@example.com')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

users = {}

def send_otp(email):
    otp = secrets.token_hex(4)  # Generate a random OTP
    users[email] = {'otp': otp, 'attempts': 0}

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg['Subject'] = 'Your OTP for login'
    msg.attach(MIMEText(otp, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        smtp_password = os.environ.get('EMAIL_PASSWORD', None)
        if smtp_password is None:
            return jsonify({'error': 'Email password not set'}), 500
        server.starttls()
        server.login(EMAIL_ADDRESS, smtp_password)
        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())

def verify_otp(email, otp):
    if email in users and users[email]['otp'] == otp:
        del users[email]  # Clear the OTP after verification
        return True
    else:
        if email in users:
            users[email]['attempts'] += 1
            if users[email]['attempts'] >= 3:
                del users[email]  # Remove user data if attempts exceed threshold
        return False

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if email in users:
        if verify_otp(email, password):  # Here, password is treated as the OTP for simplicity
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Invalid OTP or user not found'}), 401
    else:
        send_otp(email)
        return jsonify({'message': 'OTP sent to your email'}), 200

if __name__ == '__main__':
    app.run(debug=False)
