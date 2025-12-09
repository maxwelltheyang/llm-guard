import os
import datetime
import jwt
from flask import Flask, jsonify, make_response, request
from functools import wraps
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets

app = Flask(__name__)

# Use environment variable for SECRET_KEY with fallback
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

# Set DEBUG mode through environmental variables or configuration files
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    if users.get(auth.username) and users[auth.username]['password'] == auth.password:
        token = generate_token(auth.username)
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

@app.route('/protected')
@token_required
def protected():
    message = "Access granted"
    if request.is_admin:
        message += ", you are an admin."
    else:
        message += ", you are not an admin."
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode during development for easier debugging
