import os
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Set DEBUG mode based on environment variable FLASK_DEBUG
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))

# In-memory storage for tracking failed attempts and lockouts
lockout_store = {}  # {user_id: (failure_count, timestamp)}

def get_or_create_lockout(user_id):
    if user_id not in lockout_store:
        lockout_store[user_id] = (0, time.time())
    return lockout_store[user_id]

def increment_failed_attempts(user_id):
    count, timestamp = get_or_create_lockout(user_id)
    count += 1
    if count >= LOCKOUT_THRESHOLD:
        # Lock the account for a specified duration
        lockout_store[user_id] = (count, time.time() + LOCKOUT_DURATION)
    else:
        lockout_store[user_id] = (count, timestamp)
    return count

def is_account_locked(user_id):
    count, expiration_time = get_or_create_lockout(user_id)
    return expiration_time > time.time()

def reset_lockout(user_id):
    lockout_store[user_id] = (0, time.time())

# Use environment variables for LOCKOUT_THRESHOLD and LOCKOUT_DURATION with defaults
LOCKOUT_THRESHOLD = int(os.getenv('LOCKOUT_THRESHOLD', 5))
LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', 300))

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    user_id = data.get('user_id')
    entered_code = data.get('entered_code')

    if not user_id or not entered_code:
        return jsonify({"error": "Missing user_id or code"}), 400

    if is_account_locked(user_id):
        return jsonify({"error": "Account locked"}), 423

    # Fetch valid codes for the user from a secure source (e.g., AWS Secrets Manager, database)
    secret = os.getenv('TWOFA_SECRET')
    if not secret:
        raise ValueError("Valid codes not found")

    valid_codes = [code.strip() for code in secret.split(',')]

    if entered_code not in valid_codes:
        increment_failed_attempts(user_id)
        return jsonify({"error": "Invalid code"}), 401

    # Reset lockout on successful authentication
    reset_lockout(user_id)

    return jsonify({"message": "Authentication successful"})

if __name__ == '__main__':
    app.run()
