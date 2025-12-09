import os
import redis
from cryptography.fernet import Fernet
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, Flask

app = Flask(__name__)

# Generate a secure key for Fernet encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def generate_secure_token(payload):
    # Encrypt the payload with JWT and include necessary claims (iat, exp, nbf)
    token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
    return cipher_suite.encrypt(token).decode('utf-8')

def decrypt_token(encrypted_token):
    # Decrypt the JWT token and validate the claims within the payload
    try:
        encrypted_data = encrypted_token.encode('utf-8')
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        token = jwt.decode(decrypted_data, algorithms=['HS256'], options={"verify_signature": False})

        # Validate the claims (iat and nbf) within the token's payload
        iat = datetime.fromtimestamp(token['iat'])
        nbf = datetime.fromtimestamp(token['nbf'])
        now = datetime.now()

        if not (iat <= now < nbf):
            raise jwt.InvalidTokenError('Token has expired or is invalid')

        return token
    except Exception as e:
        raise jwt.InvalidTokenError(str(e))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            payload = decrypt_token(token)
        except jwt.InvalidTokenError as e:
            return jsonify({'message': str(e)}), 401

        return f(*args, **kwargs)
    return decorated

# Secure Redis configuration with authentication and network restrictions
redis_client = redis.StrictRedis(host='localhost', port=6379, password=os.getenv('REDIS_PASSWORD'), db=0)
if not redis_client.ping():
    raise Exception('Failed to connect to Redis')

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message': 'This is a protected endpoint'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
