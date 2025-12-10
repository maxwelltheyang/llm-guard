from flask import Flask, render_template, request, redirect, url_for, jsonify
from functools import wraps
import os
import jwt
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user

app = Flask(__name__)

# Store secret keys securely in environment variables
secret_key_jwt = os.environ.get("JWT_SECRET_KEY")
secret_key_bcrypt = os.environ.get("SECRET_BCRYPT_KEY")

# Database connection string from environment variable
database_uri = os.environ.get("DATABASE_URI", "sqlite:///example.db")

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
        return User.query.get(user_id)
    except (ValueError, TypeError):
        return None

@app.errorhandler(404)
def page_not_found(e):
    return "Error: Page not found", 404

# Set up logging mechanism
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)

@security.login_user_loader
def load_user_from_db(username):
    user = User.query.filter_by(email=username).first()
    return user

def validate_token(token, user_id):
    try:
        payload = jwt.decode(token, secret_key_jwt, algorithms=["RS256"])
        if payload['user_id'] != str(user_id):
            return False
        return True
    except jwt.ExpiredSignatureError:
        return False  # Token has expired
    except jwt.InvalidTokenError:
        return False  # Invalid token

def encrypt_data(data):
    cipher_suite = Fernet(os.environ.get("ENCRYPTION_KEY"))
    encrypted_data = cipher_suite.encrypt(str.encode(data))
    return encrypted_data.decode()

@app.route('/reset_password', methods=['POST'])
@login_required
def reset_password():
    try:
        token_data = request.form.get('data')
        user_id = current_user.id
        if not validate_token(token_data, user_id):
            logging.warning("Unauthorized access attempt")
            return "Error: Unauthorized access"

        user = User.query.get(user_id)
        user.reset_password()
        encrypted_password = encrypt_data(user.password)
        # Update database with encrypted password
        # (This is a simplified example and should not be used in production)
        db.session.commit()
        logging.info("User password reset successfully")
        return "Password has been successfully reset"
    except SQLAlchemy.exc.DBAPIError as e:
        logging.error(f"Database error: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=False)
