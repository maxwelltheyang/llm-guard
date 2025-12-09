import os
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# Load secret key from environment variable
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("Secret key is not set")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")

@app.route('/protected')
def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Missing or invalid Authorization header'}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = verify_token(token)
    except ValueError as e:
        return jsonify({'message': str(e)}), 401

    return jsonify({'message': 'This is a protected endpoint'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
