from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration for SQLAlchemy and Flask-Mail using environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'you@example.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # No default, should raise an exception if not set

mail = Mail(app)
db = SQLAlchemy(app)

# Constants for brute-force protection and 2FA
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
MAX_OTP_ATTEMPTS = 3
OTP_EXPIRATION_MINUTES = 5
PASSWORD_EXPIRATION_DAYS = 90

# Model to store OTP
class TwoFactorCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)  # Track OTP attempts

# Model to store login attempts
class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(80), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    successful = db.Column(db.Boolean, default=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Mock user data; add password_last_reset to track password age
users_db = {
    'user1': {
        'password': generate_password_hash('password123'),
        'email': 'user1@example.com',
        'password_last_reset': datetime.now() - timedelta(days=91)  # purposely old for testing
    }
}

# Function to send email
def send_otp(email, otp):
    msg = Message('Your OTP Code', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP code is {otp}'
    mail.send(msg)

# Function to check if a lockout is necessary
def is_locked_out(username, ip):
    cutoff = datetime.now() - LOCKOUT_DURATION
    attempts = LoginAttempt.query.filter(
        (LoginAttempt.username == username) | (LoginAttempt.ip_address == ip),
        LoginAttempt.timestamp > cutoff
    ).count()
    failed_attempts = LoginAttempt.query.filter(
        ((LoginAttempt.username == username) | (LoginAttempt.ip_address == ip)),
        LoginAttempt.timestamp > cutoff,
        LoginAttempt.successful == False
    ).count()
    return failed_attempts >= MAX_FAILED_ATTEMPTS, attempts

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    ip_address = request.remote_addr
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_db.get(username)
        if user:
            if (datetime.now() - user['password_last_reset']).days > PASSWORD_EXPIRATION_DAYS:
                flash('Password expired. Please reset your password.')
                return redirect(url_for('reset_password'))

            locked_out, _ = is_locked_out(username, ip_address)
            if locked_out:
                flash('Too many failed login attempts. Please try again later.')
                return render_template('login.html')

            if check_password_hash(user['password'], password):
                session['username'] = username
                db.session.add(LoginAttempt(ip_address=ip_address, username=username, successful=True))
                db.session.commit()

                # Generate OTP
                otp = ''.join(secrets.choice('0123456789') for _ in range(6))
                expiration_time = datetime.now() + timedelta(minutes=OTP_EXPIRATION_MINUTES)
                two_factor_code = TwoFactorCode(username=username, otp=otp, expiration=expiration_time)

                # Store OTP in the database
                db.session.add(two_factor_code)
                db.session.commit()

                send_otp(user['email'], otp)
                return redirect(url_for('verify_otp'))

        # Log the failed attempt
        db.session.add(LoginAttempt(ip_address=ip_address, username=username))
        db.session.commit()
        flash('Invalid username or password')
    return render_template('login.html')

# Route for OTP verification
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        username = session.get('username')

        if username:
            # Retrieve the OTP from the database
            two_factor_code = TwoFactorCode.query.filter_by(username=username).first()
            if two_factor_code and two_factor_code.expiration > datetime.now():
                if two_factor_code.attempts >= MAX_OTP_ATTEMPTS:
                    flash('Too many incorrect OTP entries. A new OTP is required.')
                    db.session.delete(two_factor_code)
                    db.session.commit()
                    return redirect(url_for('login'))

                if two_factor_code.otp == otp:
                    db.session.delete(two_factor_code)
                    db.session.commit()
                    flash('Login successful')
                    return redirect(url_for('dashboard'))
                else:
                    two_factor_code.attempts += 1
                    db.session.commit()
                    flash('Invalid OTP')

        flash('Invalid or expired OTP')
    return render_template('verify_otp.html')

# Dummy password reset function
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = session.get('username')
        new_password = request.form['new_password']
        if username in users_db:
            users_db[username]['password'] = generate_password_hash(new_password)
            users_db[username]['password_last_reset'] = datetime.now()
            flash('Password has been reset. Please log in with your new password.')
            return redirect(url_for('login'))
    return render_template('reset_password.html')

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
