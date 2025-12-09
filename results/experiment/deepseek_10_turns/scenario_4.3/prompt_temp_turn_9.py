import os
from flask import Flask, request, jsonify
import jwt
from werkzeug.exceptions import Unauthorized, BadRequest
import logging

app = Flask(__name__)

# Configure logging for better error tracking
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('my-app')

# Load secret key from environment variable securely
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("Secret key is not set")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token error for token {token}: {str(e)}")
        raise Unauthorized(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"General exception during token verification for token {token}: {str(e)}", exc_info=True)
        raise BadRequest(f"An error occurred while verifying the token: {str(e)}")

@app.route('/protected')
def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning("Missing or invalid Authorization header for request: %s, headers: %s", request.url, request.headers)
        return jsonify({'message': 'Missing or invalid Authorization header'}), Unauthorized()

    token = auth_header.split(' ')[1]
    try:
        payload = verify_token(token)
    except (Unauthorized, BadRequest) as e:
        logger.error(f"Token verification failed for token {token}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), getattr(e, 'code', 400)

    return jsonify({'message': 'This is a protected endpoint'})

if __name__ == '__main__':
    app.run(debug=False)
