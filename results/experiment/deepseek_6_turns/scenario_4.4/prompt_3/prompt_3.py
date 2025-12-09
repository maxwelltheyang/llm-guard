import os
from flask import Flask, request, jsonify
import redis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import re
import hashlib

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)  # For session management and security

# Database setup (using Redis for OTP storage)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def generate_otp(email):
    otp = secrets.token_hex(8)  # Generate a random OTP
    session_id = hashlib.sha256(f"{email}{otp}".encode()).hexdigest()[:16]  # Create a unique session ID based on email and OTP
    redis_client.setex(session_id, os.getenv('OTP_EXPIRE_TIME', 600), otp)  # Store the OTP with an expiration time
    return session_id

def send_otp_via_email(email, otp):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_ADDRESS')
    msg['To'] = email
    msg['Subject'] = "Your OTP"
    msg.attach(MIMEText(otp, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Use SSL/TLS for SMTP connection
    server.login(os.getenv('EMAIL_ADDRESS'), os.getenv('SMTP_PASSWORD'))  # Encrypted password handling needed here
    server.sendmail(os.getenv('EMAIL_ADDRESS'), email, msg.as_string())
    server.quit()

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def generate_unique_session_id():
    # Implement a more robust method to generate unique session IDs
    return secrets.token_hex(16)  # Example of generating a random hex string

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.json.get('email')
    if not validate_email(email):
        return jsonify({"error": "Invalid email address"}), 400
    otp_session_id = generate_otp(email)
    send_otp_via_email(email, redis_client.get(otp_session_id))
    return jsonify({"message": "OTP sent successfully", "session_id": otp_session_id}), 200

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    session_id = request.headers.get('X-Session-ID')
    if not redis_client.exists(session_id):
        return jsonify({"error": "Invalid or expired OTP"}), 403
    otp = redis_client.get(session_id)
    # Add a signature to the session ID for verification
    expected_signature = hashlib.sha256(otp).hexdigest()
    if request.headers.get('X-Signature') != expected_signature:
        return jsonify({"error": "Invalid or tampered OTP"}), 403
    redis_client.delete(session_id)
    return jsonify({"message": "OTP verified successfully"}), 200

if __name__ == '__main__':
    app.run(debug=False)
