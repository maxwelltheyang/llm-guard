from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as uts
import os

# Load the secret key from a secure environment variable.
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

bcrypt = Bcrypt(app)
app.config['BCRYPT_WORK_FACTOR'] = 13

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

class Config:
    DEBUG = False
    SECRET_KEY = os.urandom(24)

if __name__ == '__main__':
    # Set debug=False in production environments.
    app.run(debug=Config.DEBUG)
