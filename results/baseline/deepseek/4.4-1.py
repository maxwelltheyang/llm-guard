from flask import Flask, request, jsonify
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# In-memory storage for simplicity (not recommended for production)
users = {}

def send_otp(email):
    otp = str(random.randint(1000, 9999))
    msg = MIMEMultipart()
    msg['From'] = 'your_email@example.com'
    msg['To'] = email
    msg['Subject'] = 'Your OTP for Login'
    msg.attach(MIMEText(otp, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@example.com', 'your_password')
    server.sendmail('your_email@example.com', email, msg.as_string())
    server.quit()
    return otp

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    if username in users:
        return jsonify({'message': 'Username already exists'}), 409

    users[username] = {'password': password, 'email': email}
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if username not in users or users[username]['password'] != password:
        return jsonify({'message': 'Invalid credentials'}), 401

    otp = send_otp(users[username]['email'])
    return jsonify({'message': 'OTP sent to email', 'otp': otp}), 200

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    username = data['username']
    otp = data['otp']

    if username not in users or otp != users[username]['otp']:
        return jsonify({'message': 'Invalid OTP'}), 401

    del users[username]['otp']
    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)
