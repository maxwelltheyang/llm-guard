from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_mail import Mail, Message
import os
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration for Flask-Mail using environment variables
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'you@example.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # No default, should raise an exception if not set

mail = Mail(app)

# Mock user data
users_db = {
    'user1': {
        'password': generate_password_hash('password123'),
        'email': 'user1@example.com'
    }
}

# Function to send email
def send_otp(email, otp):
    msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP code is {otp}'
    mail.send(msg)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_db.get(username)
        if user and check_password_hash(user['password'], password):
            # Generate OTP
            otp = ''.join(secrets.choice('0123456789') for _ in range(6))
            session['otp'] = otp
            session['username'] = username

            send_otp(user['email'], otp)
            return redirect(url_for('verify_otp'))

        flash('Invalid username or password')
    return render_template('login.html')

# Route for OTP verification
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']

        if session.get('otp') == otp:
            session.pop('otp')
            flash('Login successful')
            return redirect(url_for('dashboard'))

        flash('Invalid OTP')
    return render_template('verify_otp.html')

# Dummy dashboard page
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome to your dashboard, {session['username']}!"
    return redirect(url_for('login'))

# Run the application
if __name__ == '__main__':
    # Debug mode is controlled by an environment variable
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 't')
    app.run(debug=debug_mode)
