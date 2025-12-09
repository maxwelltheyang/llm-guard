import os
import time
from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
from threading import Lock

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')  # Use a secure method to set a secret key

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.example.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = bool(os.environ.get('MAIL_USE_TLS', True))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your_email@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Securely set email password
mail = Mail(app)

# Mock user data (usually stored in a database)
users = {
    "testuser": {
        "password": generate_password_hash("TestPassword123"),
        "email": "testuser@example.com"
    }
}

# Temporary in-memory store for OTPs (in a real application, use a database)
otp_store = {}
otp_lock = Lock()

def send_otp(email, otp):
    try:
        msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Your one-time password (OTP) is: {otp}'
        mail.send(msg)
    except Exception as e:
        print("Error: unable to send email", e)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and check_password_hash(user['password'], password):
            otp = ''.join(secrets.choice('0123456789') for _ in range(6))  # Use the secrets module for secure OTP

            with otp_lock:
                otp_store[username] = {'otp': otp, 'timestamp': time.time()}

            send_otp(user['email'], otp)  # Send OTP to user's email
            session['username'] = username
            return redirect(url_for('verify_otp'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        entered_otp = request.form['otp']

        with otp_lock:
            otp_info = otp_store.get(username)
            current_time = time.time()

            if otp_info and entered_otp == otp_info['otp'] and (current_time - otp_info['timestamp']) < 300:
                otp_store.pop(username, None)
                flash('Login successful!')
                return redirect(url_for('protected'))

        flash('Invalid or expired OTP.')
    return render_template('verify_otp.html')

@app.route('/protected')
def protected():
    if 'username' in session:
        return f"Welcome, {session['username']}! You have successfully logged in."
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()  # Ensure debug=False for production
