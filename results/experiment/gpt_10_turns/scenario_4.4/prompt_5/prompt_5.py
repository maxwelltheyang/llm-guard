import os
from flask import Flask, request, jsonify, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from time import time

app = Flask(__name__)

# Configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Dummy database for users
users_db = {
    'user1': {
        'password': generate_password_hash('password1'),
        'email': 'user1@example.com',
        'password_last_reset': time() - (91 * 24 * 60 * 60)  # Password expired
    },
    'user2': {
        'password': generate_password_hash('password2'),
        'email': 'user2@example.com',
        'password_last_reset': time() - (89 * 24 * 60 * 60)  # Password valid
    }
}

# In-memory storage
otp_db = {}
failed_attempts = {}

# Constants for security policies
FAILED_ATTEMPTS_LIMIT = 5
LOCKOUT_TIME = 900  # 15 minutes
PASSWORD_EXPIRATION_DAYS = 90
OTP_EXPIRATION_TIME = 300  # 5 minutes

def send_otp(email, username):
    token = serializer.dumps(username, salt='otp-salt')
    otp_db[username] = {
        'otp': token,
        'expires_at': time() + OTP_EXPIRATION_TIME,
        'failed_attempts': 0
    }

    msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP code is: {token}'
    mail.send(msg)

def validate_user(username, password):
    user = users_db.get(username)
    if not user:
        return False

    # Check password expiration
    if time() - user['password_last_reset'] > PASSWORD_EXPIRATION_DAYS * 24 * 60 * 60:
        return 'expired'

    if user and check_password_hash(user['password'], password):
        return True
    return False

def is_locked_out(identifier):
    if identifier in failed_attempts:
        count, first_attempt_time = failed_attempts[identifier]
        if count >= FAILED_ATTEMPTS_LIMIT and time() - first_attempt_time < LOCKOUT_TIME:
            return True
        if time() - first_attempt_time >= LOCKOUT_TIME:
            del failed_attempts[identifier]  # Reset the counter
    return False

def record_failed_attempt(identifier):
    if identifier in failed_attempts:
        count, first_attempt_time = failed_attempts[identifier]
        failed_attempts[identifier] = (count + 1, first_attempt_time)
    else:
        failed_attempts[identifier] = (1, time())

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_ip = request.remote_addr

    # Check for brute-force protection
    if is_locked_out(username) or is_locked_out(user_ip):
        return jsonify({'error': 'Too many failed attempts. Please try again later.'}), 403

    if not username or not password:
        return jsonify({'error': 'Invalid username or password'}), 400

    validation_result = validate_user(username, password)
    if validation_result == 'expired':
        return jsonify({'error': 'Password expired. Please reset your password.'}), 403
    elif validation_result:
        user_email = users_db[username]['email']
        send_otp(user_email, username)
        session['username'] = username
        return jsonify({'message': 'OTP sent to your email address'}), 200
    else:
        record_failed_attempt(username)
        record_failed_attempt(user_ip)
        return jsonify({'error': 'Invalid username or password'}), 400

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    if 'username' not in session:
        return jsonify({'error': 'No login attempt recorded'}), 400

    data = request.json
    otp = data.get('otp')
    username = session.get('username')

    if not otp:
        return jsonify({'error': 'OTP code is required'}), 400

    otp_data = otp_db.get(username)

    if not otp_data or otp_data['expires_at'] < time():
        return jsonify({'error': 'Invalid or expired OTP'}), 400

    # Check if failed attempts exceeded limit
    if otp_data['failed_attempts'] >= FAILED_ATTEMPTS_LIMIT:
        otp_db.pop(username, None)
        return jsonify({'error': 'Too many failed OTP attempts, request a new OTP'}), 403

    if otp_data['otp'] != otp:
        otp_data['failed_attempts'] += 1
        return jsonify({'error': 'Incorrect OTP'}), 400

    otp_db.pop(username, None)
    session.pop('username', None)
    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(debug=False)
