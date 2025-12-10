from flask import Flask, render_template, request, redirect, url_for, jsonify
from functools import wraps
import os
import jwt
from passlib.context import CryptContext
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)

# Production configuration: Set debug to False for production environments using environment variables
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG') == 'True'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the secret key for token generation
jwt_secret_key = app.config['JWT_SECRET_KEY']

# Initialize Flask-Login with a custom user loader function
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Set login view

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define a function to verify tokens and get the user ID from them
def get_user_id_from_token(token):
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except Exception as e:
        import logging
        logging.error(f"Error verifying token: {str(e)}")
        return None

# Define a decorator for requiring authentication with token expiration (1 hour)
def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing Authorization Header'}), 401
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            # Check if the token is expired
            if payload['exp'] < int(time.time()):
                return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
        except Exception as e:
            import logging
            logging.error(f"Error in token verification: {str(e)}")
            return jsonify({'message': 'Internal Server Error'}), 500
        return f(*args, **kwargs)
    return decorated_function

# Refresh endpoint to generate new access tokens upon user authentication
@app.route('/refresh_token', methods=['POST'])
def refresh_token():
    try:
        token = request.json['token']
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        # Assuming you have a login function that returns a new access token
        # Replace this with your actual implementation
        return jsonify({'access_token': 'new_access_token'})
    except Exception as e:
        import logging
        logging.error(f"Error in refresh token endpoint: {str(e)}")
        return jsonify({'message': 'Internal Server Error'}), 500

@app.route('/protected_route', methods=['GET'])
@requires_auth
def protected_route():
    # This route is now accessible only after authentication
    return jsonify({'message': 'Hello, world!'})

if __name__ == '__main__':
    app.run()
