from flask import Flask, request, jsonify, g, logging
import jwt
import os
import datetime

app = Flask(__name__)

# Load secret key from environment variable for production use
SECRET_KEY = os.getenv('SECRET_KEY', 'your-256-bit-secret')

# Configure logging for security audits and detailed error messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logger.warning("Authentication failed: No token provided.")
            return jsonify({"error": "Missing authorization header"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Check token expiration and ensure it's not expired
            if 'exp' in payload and datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(payload['exp']):
                logger.error("Authentication failed: Expired token detected.")
                return jsonify({"error": "Token has expired"}), 401

            g.user = payload['sub']  # Assuming 'sub' contains the username or user ID
            g.admin = payload.get('admin', False)  # Adding admin flag to global context
        except jwt.ExpiredSignatureError:
            logger.error("Authentication failed: Expired token detected.")
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            logger.error("Authentication failed: Invalid token detected.")
            return jsonify({"error": "Invalid token"}), 401

        logger.info(f"User {g.user} successfully authenticated.")
        return func(*args, **kwargs)
    return wrapper

@app.route('/protected', methods=['GET'])
@authenticate
def protected_endpoint():
    return jsonify({'message': f'Hello, {g.user}! You have access to this protected route.', 'admin': g.admin})

if __name__ == '__main__':
    app.run(debug=False)
