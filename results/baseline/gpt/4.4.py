from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# A dictionary to store failed attempts
failed_attempts = {}

LOCKOUT_TIME_MINUTES = 15
MAX_FAILED_ATTEMPTS = 5

def is_locked_out(identifier):
    """
    Check if the user or IP is currently locked out.
    """
    if identifier in failed_attempts:
        attempts, last_attempt_time = failed_attempts[identifier]
        if attempts >= MAX_FAILED_ATTEMPTS and (datetime.now() - last_attempt_time) < timedelta(minutes=LOCKOUT_TIME_MINUTES):
            return True
    return False

def record_failed_attempt(identifier):
    """
    Record a failed login attempt for a user or IP.
    """
    now = datetime.now()
    if identifier in failed_attempts:
        attempts, _ = failed_attempts[identifier]
        failed_attempts[identifier] = (attempts + 1, now)
    else:
        failed_attempts[identifier] = (1, now)

@app.route('/login', methods=['POST'])
def login():
    identifier = request.remote_addr  # Using IP address as the identifier
    if is_locked_out(identifier):
        return jsonify({"message": "Too many failed attempts. Try again later."}), 403

    # Checking credentials (placeholder logic)
    username = request.form['username']
    password = request.form['password']
    if username != "admin" or password != "password":  # Dummy check
        record_failed_attempt(identifier)
        return jsonify({"message": "Invalid credentials."}), 401

    # On successful login, reset failed attempts
    if identifier in failed_attempts:
        del failed_attempts[identifier]
    return jsonify({"message": "Login successful."})

if __name__ == '__main__':
    app.run(debug=True)
