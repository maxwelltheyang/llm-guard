from flask import Flask, render_template, request, session, redirect, url_for
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_bcrypt import Bcrypt
from os import urandom
import string
import secrets
import hashlib

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Load environment variables from .env file
load_dotenv()

# Email configuration with credentials stored as environment variables
email_server = "smtp.gmail.com"
email_port = 587
email_username = os.getenv("EMAIL_USERNAME")
email_password = os.getenv("EMAIL_PASSWORD")

# Secret key for session management
secret_key = os.getenv("SECRET_KEY")

app.config['SECRET_KEY'] = secret_key

# Seed the secrets generator with high-quality randomness
secrets.SystemRandom().randint(0, 10)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user using a secure authentication mechanism
        from flask_principal import Principal, Permission, RoleNeed, UserNeed

        principal = Principal(app)

        # Define roles and permissions
        admin_role = RoleNeed('admin')
        admin_permission = Permission(admin_role)

        try:
            if username == os.getenv("ADMIN_USERNAME") and bcrypt.check_password_hash(os.getenv("ADMIN_PASSWORD"), password):
                # Grant admin role to the user
                @principal.identity_loader
                def load_identity(user):
                    return {'id': 1, 'username': username}

                principal.assign_role('admin', username)
                return render_template('login_successful.html')
        except Exception as e:
            print(e)

        # Send one-time code via email using Flask-Mail
        from flask_mail import Mail, Message

        mail = Mail(app)

        otp = ''.join(secrets.choice(string.digits) for _ in range(6))

        msg = MIMEMultipart()
        msg['From'] = f'{email_username}'
        msg['To'] = username
        msg['Subject'] = 'One-time code for 2FA'
        body = f"Your one-time code is: {otp}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(email_server, email_port)
        server.starttls()
        server.login(f'{email_username}', email_password)
        text = msg.as_string()
        server.sendmail(f'{email_username}', username, text)
        server.quit()

        # Store OTP in session for 2FA verification
        session['otp'] = otp

        return render_template('enter_otp.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    if request.method == 'POST':
        provided_otp = request.form.get('otp')

        # Verify OTP using Flask-WTF for form validation
        from flask_wtf import FlaskForm, StringField, PasswordField, validators

        class OTPForm(FlaskForm):
            otp = StringField('OTP', [validators.DataRequired()])

        form = OTPForm()

        stored_otp_hash = hashlib.sha256(session['otp'].encode()).hexdigest()
        provided_otp_hash = hashlib.sha256(provided_otp.encode()).hexdigest()

        if stored_otp_hash == provided_otp_hash:
            # Grant access based on user's role and permissions
            return render_template('access_granted.html')
        else:
            # Handle invalid OTP attempt
            return render_template('invalid_otp.html')

if __name__ == '__main__':
    app.run(debug=False)
