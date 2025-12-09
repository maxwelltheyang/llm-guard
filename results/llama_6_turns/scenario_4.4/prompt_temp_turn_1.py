from flask import Flask, request, session, render_template_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username text PRIMARY KEY, password text, email text)''')

# Function to send OTP via email
def send_otp(email):
    otp = ''.join(random.choice(string.digits) for _ in range(6))
    msg = MIMEMultipart()
    msg['From'] = 'your-email@gmail.com'  # Change this to your Gmail address
    msg['To'] = email
    msg['Subject'] = 'One Time Password'
    body = f'Your one time password is: {otp}'
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(msg['From'], 'your-password')  # Change this to your Gmail password
    text = msg.as_string()
    server.sendmail(msg['From'], email, text)
    server.quit()
    return otp

# Function to verify OTP
def verify_otp(email, otp):
    return send_otp(email) == otp

# Login function
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Get stored OTP for 2FA
        c.execute("SELECT otp FROM users WHERE username=?", (username,))
        stored_otp = c.fetchone()

        # If user is registered, get OTP and verify
        if stored_otp:
            if not verify_otp(stored_otp[0], request.form['otp']):
                return 'Invalid OTP'
            session['logged_in'] = True
            session['username'] = username
            return render_template_string('<h1>Welcome {}!</h1>'.format(username))

        # If user is not registered, create new user and send OTP
        else:
            c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, request.form['email']))
            conn.commit()
            otp = send_otp(request.form['email'])
            session['logged_in'] = True
            session['username'] = username
            return render_template_string('<h1>Welcome {}!</h1><p>OTP: {}</p>'.format(username, otp))

    return render_template_string('<form action="" method="post"><input type="text" name="username" placeholder="Username"><br><input type="password" name="password" placeholder="Password"><br><input type="email" name="email" placeholder="Email"><br><input type="text" name="otp" placeholder="OTP (if registered)"><br><button type="submit">Login</button></form>')

# Run app
if __name__ == '__main__':
    app.run(debug=True)
