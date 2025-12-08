from flask import Flask, request, jsonify
import jwt
import bcrypt
import os
from flask_sqlalchemy import SQLAlchemy
from logging.config import dictConfig

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
bcrypt.gen_salt(length=16)

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
        db.session.rollback()
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

        # Retrieve user from database
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            # Generate JWT token securely
            payload = {'user_id': user.id}
            jwt_token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')

            return jsonify({'token': str(jwt_token)}), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        app.logger.error(f"Error logging in user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def validate_userdata(username, email):
    # Validate username and email using parameterized queries or prepared statements
    pass

if __name__ == '__main__':
    app.run(debug=True)
