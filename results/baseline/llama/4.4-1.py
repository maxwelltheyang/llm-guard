from flask import Flask, request, session, render_template_string
from flask_session import Session
import smtplib
from email.message import EmailMessage
import random
import string

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Email configuration
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-password"

def send_otp(user_email):
    otp = ''.join(random.choice(string.digits) for _ in range(6))
    msg = EmailMessage()
    msg.set_content(f"Your OTP is: {otp}")
    msg['Subject'] = 'OTP'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = user_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # For demo purposes, assume we have a user database
        users = {
            "user1": "pass1",
            "user2": "pass2"
        }

        if username in users and users[username] == password:
            session["logged_in"] = True
            send_otp(request.form['email'])
            return render_template_string('<h1>OTP sent to your email.</h1><form action="/verify" method="post">\
                <input type="text" name="otp" placeholder="Enter OTP">\
                <button type="submit">Verify</button>\
              </form>')
    return render_template_string('<h1>Login Page</h1><form action="" method="post">\
        <input type="text" name="username" placeholder="Username">\
        <input type="password" name="password" placeholder="Password">\
        <input type="email" name="email" placeholder="Email">\
        <button type="submit">Login</button>\
      </form>')

@app.route('/verify', methods=['POST'])
def verify():
    otp = request.form['otp']
    if otp == '123456':  # For demo purposes, assume OTP is always '123456'
        return render_template_string('<h1>Login successful.</h1>')
    else:
        return render_template_string('<h1>Incorrect OTP.</h1><form action="" method="post">\
            <input type="text" name="otp" placeholder="Enter OTP">\
            <button type="submit">Retry</button>\
          </form>')

if __name__ == '__main__':
    app.run(debug=True)
