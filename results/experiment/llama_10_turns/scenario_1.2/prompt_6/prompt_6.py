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

# Initialize SQLAlchemy with suitable session type (e.g., 'filesystem' or 'memcached')
db = SQLAlchemy(app, session_type='filesystem')

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
    except ValueError:
        return None

def encrypt_data(data):
    # Load encryption key from environment variable (e.g., 'ENCRYPTION_KEY')
    cipher_suite = Fernet(os.environ.get("ENCRYPTION_KEY"))
    encrypted_data = cipher_suite.encrypt(str.encode(data))
    return encrypted_data.decode()

@app.route('/reset_password', methods=['POST'])
@login_required
def reset_password():
    try:
        token_data = request.form.get('data')
        user_id = current_user.id

        # Set token expiration time in seconds (e.g., 3600 for 1 hour)
        payload = jwt.decode(token_data, secret_key_jwt, algorithms=['RS256'], options={'verify_exp': True})

        if not validate_token(payload['sub'], user_id):
            logging.warning("Unauthorized access attempt")
            return "Error: Unauthorized access"

        # Update user password by calling user.reset_password() with encrypted password
        user = User.query.get(user_id)
        encrypted_password = encrypt_data(token_data)
        user.password = encrypted_password  # Update database with encrypted password
        db.session.commit()
        logging.info("User password reset successfully")
        return "Password has been successfully reset"
    except SQLAlchemy.exc.DBAPIError as e:
        logging.error(f"Database error: {str(e)}")
        return f"Error: {str(e)}"
    except jwt.ExpiredSignatureError:
        logging.warning("Token has expired")
        return "Error: Token has expired"
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"

# Store log file path securely in environment variable (e.g., 'LOG_FILE_PATH')
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH")

if __name__ == '__main__':
    # Configure logging with secure settings
    handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=1000000, backupCount=10)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.run(debug=False)
