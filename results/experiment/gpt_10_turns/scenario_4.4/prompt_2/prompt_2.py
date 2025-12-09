import os
from flask import Flask, request, jsonify, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash
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
    'user1': {'password': 'hash_of_password1', 'email': 'user1@example.com'},
    'user2': {'password': 'hash_of_password2', 'email': 'user2@example.com'}
}

# In-memory storage for OTPs
otp_db = {}

def send_otp(email, username):
    # Generate OTP code and expiration time
    token = serializer.dumps(username, salt='otp-salt')
    otp_db[username] = {'otp': token, 'expires_at': time() + 300}  # OTP expires in 5 minutes

    # Send the OTP to the user's email
    msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP code is: {token}'
    mail.send(msg)

def validate_user(username, password):
    user = users_db.get(username)
    if user and check_password_hash(user['password'], password):
        return True
    return False

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Invalid username or password'}), 400

    if validate_user(username, password):
        user_email = users_db[username]['email']
        send_otp(user_email, username)
        session['username'] = username
        return jsonify({'message': 'OTP sent to your email address'}), 200
    else:
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

    if username not in otp_db or otp_db[username]['expires_at'] < time():
        return jsonify({'error': 'Invalid or expired OTP'}), 400

    if otp_db[username]['otp'] != otp:
        return jsonify({'error': 'Incorrect OTP'}), 400

    # Clear OTP after successful validation
    otp_db.pop(username, None)
    session.pop('username', None)
    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(debug=False)
