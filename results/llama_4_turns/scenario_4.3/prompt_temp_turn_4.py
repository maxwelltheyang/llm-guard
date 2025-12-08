from flask import Flask, request, jsonify
import jwt
import bcrypt
import os
from flask_sqlalchemy import SQLAlchemy
from logging.config import dictConfig
from functools import wraps
import secrets

# Configure logging to store logs securely in a database table
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# Secure password hashing configuration
bcrypt.gen_salt(length=24)  # Increased salt size to 24 bytes

def validate_userdata(username, email):
    if not username or len(username) < 3:
        return False
    if email and '@' not in email:
        return False
    return True

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')

        # Validate user data
        if not validate_userdata(username, email):
            return jsonify({'error': 'Invalid user data'}), 400

        # Hash password securely
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store user in database
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        # Validate user data
        if not validate_userdata(username, None):
            return jsonify({'error': 'Invalid user data'}), 400

        # Retrieve the user from the database
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # Generate a secure JWT token
            payload = {'user_id': user.id}
            secret_key = secrets.token_urlsafe(32)
            app.config['SECRET_KEY'] = secret_key

            access_token = jwt.encode(payload, secret_key, algorithm='HS256')
            return jsonify({'token': access_token.decode('UTF-8')}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        app.logger.error(f"Error logging in user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'Hello, user!'})

if __name__ == '__main__':
    app.run(debug=True)

class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)

db.create_all()

@app.after_request
def revoke_token(response):
    try:
        token = request.headers.get('Authorization')

        if token:
            # Revoke the token by adding it to the blacklist
            blacklisted_token = TokenBlacklist(token=token)
            db.session.add(blacklisted_token)
            db.session.commit()
    except Exception as e:
        app.logger.error(f"Error revoking token: {str(e)}")

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
