import os
from flask import Flask, request, jsonify
import jwt
from werkzeug.exceptions import Unauthorized, BadRequest

app = Flask(__name__)

# Load secret key from environment variable securely
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("Secret key is not set")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError as e:
        raise Unauthorized(f"Invalid token: {str(e)}")
    except Exception as e:
        raise BadRequest(f"An error occurred while verifying the token: {str(e)}")

@app.route('/protected')
def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Missing or invalid Authorization header'}), Unauthorized()

    token = auth_header.split(' ')[1]
    try:
        payload = verify_token(token)
    except (Unauthorized, BadRequest) as e:
        return jsonify({'error': str(e)}), getattr(e, 'code', 400)

    return jsonify({'message': 'This is a protected endpoint'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
