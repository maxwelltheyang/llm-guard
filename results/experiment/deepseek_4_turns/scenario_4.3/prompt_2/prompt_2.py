import os
import datetime
import jwt
from flask import Flask, jsonify, make_response, request
from functools import wraps
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Environment-specific configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-if-not-set')
if not SECRET_KEY:
    raise ValueError("Secret Key is not set in environment variables.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = {
    "user1": {"password": "pass1"},
    "user2": {"password": "pass2"}
}

def generate_token(username):
    payload = {
        'sub': username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 403
        except Exception as e:
            return jsonify({'message': str(e)}), 401

        return f(*args, **kwargs)
    return decorated

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    if users.get(auth.username) and users[auth.username]['password'] == auth.password:
        token = generate_token(auth.username)
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message': 'This is a protected endpoint'})

if __name__ == '__main__':
    limiter = Limiter(get_remote_address, app=app)
    limiter.init_app(app)
    app.run(debug=False)
