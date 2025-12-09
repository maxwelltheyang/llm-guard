from flask import Flask, request, jsonify, g
import jwt
import os

app = Flask(__name__)

# Load secret key from environment variable for production use
SECRET_KEY = os.getenv('SECRET_KEY', 'your-256-bit-secret')

def authenticate(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Missing authorization header"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.user = payload['sub']  # Assuming 'sub' contains the username or user ID
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)
    return wrapper

@app.route('/protected', methods=['GET'])
@authenticate
def protected_endpoint():
    return jsonify({'message': f'Hello, {g.user}! You have access to this protected route.'})

if __name__ == '__main__':
    app.run(debug=False)
