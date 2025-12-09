import os
from flask import Flask, request, jsonify
import redis
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)  # Initialize Redis connection

# Check for required environment variables at startup
required_vars = ['EMAIL_ADDRESS', 'SMTP_SERVER', 'EMAIL_PASSWORD']
missing_vars = [var for var in required_vars if os.getenv(var) is None]
if missing_vars:
    raise ValueError(f"The following environment variables are missing: {', '.join(missing_vars)}")

def generate_otp(email):
    otp = secrets.token_hex(3)  # Generate a random OTP for simplicity in this example
    session_id = str(uuid.uuid4())  # Create a unique session ID for each OTP
    redis_client.hmset(session_id, {'otp': otp, 'email': email})
    redis_client.expire(session_id, 600)  # Set the session to expire in 10 minutes (adjust as needed)
    return otp

def send_otp_via_email(email, otp):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_ADDRESS')
    msg['To'] = email
    msg['Subject'] = 'Your OTP'
    msg.attach(MIMEText(f"Your OTP is: {otp}", 'plain'))

    server = smtplib.SMTP(os.getenv('SMTP_SERVER'), 587)
    server.starttls()
    try:
        server.login(os.getenv('EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD'))
        server.sendmail(os.getenv('EMAIL_ADDRESS'), email, msg.as_string())
    except Exception as e:
        print(f"Failed to send OTP via email: {e}")
        return False
    finally:
        server.quit()
    return True

def verify_otp(email, otp):
    session_id = redis_client.hgetall(f"otp:{email}")  # Fetch OTP by email from Redis
    if not session_id:
        return False
    stored_otp = session_id.get('otp')
    if stored_otp is None or stored_otp != otp:
        return False
    redis_client.delete(session_id)  # Expire and delete the OTP data after verification
    return True

@app.route('/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    email = request.json.get('email')
    otp = request.json.get('otp')
    if not email or not otp:
        return jsonify({'status': 'failed', 'reason': 'Missing required fields'}), 400

    if not verify_otp(email, otp):
        return jsonify({'status': 'failed', 'reason': 'Invalid OTP'}), 400
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run()
