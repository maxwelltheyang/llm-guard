from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from passlib.context import CryptContext
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  
jwt = JWTManager(app)

# Load environment variables securely
import dotenv
dotenv.load_dotenv()

# Don't commit .env files to your repository for security reasons
# Consider using a secrets management tool like Hashicorp's Vault
# For this example, let's assume we have a separate secrets file

secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.env')
if os.path.exists(secrets_path):
    dotenv.load_dotenv(secrets_path)

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 1024*1024*10, # 10MB
            'backupCount': 1,
            'level': 'INFO',
            'formatter': 'default'
        }
    },
    'root': {
        'handlers': ['wsgi', 'file'],
        'level': 'INFO' # Changed from DEBUG to INFO
    }
})

# Enhanced Input Validation
def validate_input(data):
    if not isinstance(data['username'], str) or not data['username'].isalnum():
        raise ValueError("Username must be alphanumeric")
    if len(data['password']) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(char.isupper() for char in data['password']):
        raise ValueError("Password must contain an uppercase letter")
    if not any(char.isdigit() for char in data['password']):
        raise ValueError("Password must contain a digit")

# Password Policy Enforcement
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], default='pbkdf2_sha256')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/register', methods=['POST'])
@limiter.limit("10/minute") # Increased rate limit for registration
def register():
    data = request.json
    validate_input(data)
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({'error': 'Username already taken'}), 400
    hashed_password = pwd_context.hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 200

@app.route('/change-password', methods=['POST'])
@limiter.limit("10/minute") # Increased rate limit for changing passwords
@jwt_required() # Requires valid access token to change password
def change_password():
    data = request.json
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    if not pwd_context.verify(data['old_password'], current_user.password):
        return jsonify({'error': 'Invalid old password'}), 401
    new_hashed_password = pwd_context.hash(data['new_password'])
    current_user.password = new_hashed_password
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'}), 200

# Login Logic with Brute-Force Protection
@app.route('/login', methods=['POST'])
@limiter.limit("10/minute") # Increased rate limit for login attempts
def login():
    data = request.json
    validate_input(data)
    user = User.query.filter_by(username=data['username']).first()
    if not user or not pwd_context.verify(data['password'], user.password):
        return jsonify({'error': 'Invalid username or password'}), 401
    access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(minutes=30)) # Token expiration time increased to 30 minutes
    return jsonify(access_token=access_token), 200

# Session Expiration and Revocation (Token Blacklisting)
from flask_jwt_extended import get_raw_jwt, jwt_required, jwt_blacklist_tokens

@app.route('/logout', methods=['POST'])
@jwt_required() # Requires valid access token to logout
def logout():
    jti = get_raw_jwt()['jti'] # Get the JWT ID
    blacklist_tokens(jti) # Add the JWT ID to the blacklist
    return jsonify({'message': 'You have been logged out'}), 200

if __name__ == '__main__':
    from OpenSSL import crypto
    from ssl import SSLContext, PROTOCOL_TLSv1_2

    cert_path = os.environ.get('CERT_PATH')
    key_path = os.environ.get('KEY_PATH')

    if not cert_path or not key_path:
        raise ValueError("Missing required environment variables")

    cert = crypto.load_certificate(crypto.FILETYPE_PEM,
        open(cert_path).read())
    key = crypto.load_privatekey(crypto.FILETYPE_PEM,
        open(key_path).read())

    ssl_context = SSLContext(PROTOCOL_TLSv1_2)
    ssl_context.load_cert_chain(cert, key)

    app.run(host='127.0.0.1', port=5000, ssl_context=ssl_context)
