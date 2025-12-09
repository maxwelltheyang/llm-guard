import os
from flask import Flask, request, jsonify
import jwt
from functools import wraps
from cryptography.fernet import Fernet

app = Flask(__name__)

# Set default value for SECRET_KEY from environment variables with validation
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    raise ValueError("SECRET_KEY must be set in the environment variables.")

# Validate that the SECRET_KEY is strong enough
def validate_secret_key(secret_key):
    if len(secret_key) < 32:  # Common minimum length for secure keys
        raise ValueError("SECRET_KEY must be at least 32 characters long.")
    return secret_key

# Use a key management service or hardware security module (HSM) to securely manage the SECRET_KEY.
app.config['SECRET_KEY'] = validate_secret_key(secret_key).encode()

# Set debug mode based on environment variable, default to False
debug_mode = bool(os.getenv('FLASK_ENV', 'False'))
app.config['DEBUG'] = debug_mode

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = list(filter(lambda x: x["username"] == data["sub"], authorized_users))

            if not current_user:
                return jsonify({'message': 'Token is invalid'}), 403
        except Exception as e:
            print(e)
            return jsonify({'message': 'Token is invalid'}), 403

        return f(*args, **kwargs)
    return decorated

@app.route('/write', methods=['POST'])
@token_required
def write():
    data = request.get_json()
    # Process the write operation here
    return jsonify({'message': 'Write operation successful'}), 200

@app.route('/export', methods=['GET'])
@token_required
def export():
    # Perform the export operation here
    return jsonify({'data': 'some exported data'})

if __name__ == '__main__':
    app.run()
