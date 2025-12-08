from flask import Flask, request, render_template, redirect, url_for, session
from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'you@example.com'
app.config['MAIL_PASSWORD'] = 'yourpassword'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

users = {'user': 'password'}  # Example users

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            otp = generate_otp()
            session['otp'] = otp
            session['username'] = username

            msg = Message('Your OTP Code', sender='you@example.com', recipients=[f'{username}@example.com'])
            msg.body = f'Your OTP code is {otp}'
            mail.send(msg)

            return redirect(url_for('validate_otp'))

    return render_template('login.html')

@app.route('/validate_otp', methods=['GET', 'POST'])
def validate_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        if 'otp' in session and session['otp'] == otp:
            return 'Logged in successfully'
        else:
            return 'Invalid OTP'

    return render_template('validate_otp.html')

if __name__ == '__main__':
    app.run(debug=True)
