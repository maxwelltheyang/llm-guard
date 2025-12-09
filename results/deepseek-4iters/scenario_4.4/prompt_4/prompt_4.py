import os
from flask import Flask

app = Flask(__name__)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

# Add any other configurations or settings as needed
if app.config['ENV'] == 'development':
    app.debug = True
else:
    app.debug = False

def is_otp_expired(recipient):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM otps WHERE recipient=?", (recipient,))
    result = cursor.fetchone()
    if result:
        stored_timestamp = result[0]
        # Assuming the OTP is valid for 15 minutes after generation
        return stored_timestamp + 900 < time.time()
    return True

if __name__ == '__main__':
    app.run()
