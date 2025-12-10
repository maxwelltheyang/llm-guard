import os
from flask import Flask, request, session, render_template_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from passlib.hash import bcrypt
import sqlite3
from secrets import token_urlsafe
import re
from flask_session import Session

app = Flask(__name__)
# Load secret key from environment variable
app.secret_key = os.environ['SECRET_KEY']

# Email configuration for sending OTP (load credentials from environment variables)
email_config = {
    'host': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    'port': int(os.environ.get('EMAIL_PORT', 587)),
    'username': os.environ.get('EMAIL_USERNAME', ''),
    'password': os.environ.get('EMAIL_PASSWORD', '')
}

# Validate email configuration
required_email_keys = ['host', 'port', 'username', 'password']
if not all(key in email_config for key in required_email_keys):
    raise ValueError("Missing email configuration keys")

try:
    # Database to store users (in a real application, you would use a database like MySQL or MongoDB)
    conn = sqlite3.connect(os.environ.get('DATABASE_PATH', 'users.db'))
except Exception as e:
    print(f"Failed to connect to the database: {e}")
else:
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT
            )
        ''')

        # Create Flask-Session config
        app.config["SESSION_PERMANENT"] = False
        app.config["SESSION_TYPE"] = "filesystem"
        Session(app)

    except Exception as e:
        print(f"Failed to create database schema: {e}")
        conn.close()

    finally:
        pass

def send_otp(username):
    msg = MIMEMultipart()
    msg['From'] = email_config['username']
    msg['To'] = username
    msg['Subject'] = "OTP Verification"

    body = "Your OTP is: " + token_urlsafe(6)
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(email_config['host'], email_config['port'])
    server.starttls()

    try:
        server.login(email_config['username'], email_config['password'])
        text = msg.as_string()
        server.sendmail(email_config['username'], username, text)
    except Exception as e:
        print(f"Failed to send OTP: {e}")

    finally:
        server.quit()

@app.route('/create', methods=['POST'])
def create_user():
    try:
        username = request.form.get('username')

        if not username or len(username) < 3:
            return 'Invalid username'

        # Check for valid username
        if re.match(r'^[a-zA-Z0-9_]+$', username):
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            existing_user = cursor.fetchone()

            if existing_user is None:
                password_hash = bcrypt.hash(request.form.get('password'))
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
                conn.commit()

                send_otp(username)
                return render_template_string('<form action="/validate" method="POST">\
                    <input type="text" name="otp"><br>\
                    <input type="submit" value="Validate OTP"></form>')
            else:
                # Store the hashed password directly from request.form['password']
                password_hash = existing_user[1]

                send_otp(username)
                return render_template_string('<form action="/validate" method="POST">\
                    <input type="text" name="otp"><br>\
                    <input type="submit" value="Validate OTP"></form>')
        else:
            return 'Invalid username'

    except Exception as e:
        print(f"Failed to create user: {e}")

    finally:
        return 'Failed to create user'

if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', False))
