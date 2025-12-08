from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer as uts
import os

app = Flask(__name__)
# Use a secure environment variable for the secret key.
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

bcrypt = Bcrypt(app)
app.config['BCRYPT_WORK_FACTOR'] = 13

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

class Config:
    DEBUG = False

if __name__ == '__main__':
    # Set debug=False in production environments.
    app.run(debug=Config.DEBUG)
