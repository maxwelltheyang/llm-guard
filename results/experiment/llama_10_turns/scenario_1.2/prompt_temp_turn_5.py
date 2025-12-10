from flask import Flask, render_template, request, redirect, url_for, jsonify
from functools import wraps
import os
import jwt
from passlib.context import CryptContext
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)

# Store secret keys securely in environment variables
secret_key_jwt = os.environ.get("JWT_SECRET_KEY")
secret_key_flask_security = os.environ.get("FLASK_SECURITY_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bcrypt_context = CryptContext(schemes=["argon2"], default="argon2", bcrypt__rounds=14, arg2__salt_max_bytes=32, arg2__salt_min_bytes=16)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    password_reset_token = db.Column(db.String(128), nullable=True, unique=True)
    last_password_reset = db.Column(db.DateTime, nullable=True)
    password_reset_expires_at = db.Column(db.DateTime, nullable=True)

    def reset_password(self):
        self.last_password_reset = datetime.now()
        expires_in_minutes = 30
        self.password_reset_expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)  
        try:
            db.session.commit()
            return True
        except Exception as e:
            app.logger.error(f"Error resetting password for user {self.id}: {str(e)}")
            raise PasswordResetError(str(e))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))

@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except Exception as e:
        app.logger.error(f"Error loading user with ID {id}: {str(e)}")
        if isinstance(e, sqlalchemy.exc.NoResultFound):
            app.logger.warning(f"No user found with ID {id}")
            return None
        else:
            raise

@app.route('/reset_password', methods=['GET'])
def reset_password_get():
    expires_in_minutes = 30
    token_expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
    return render_template('reset_password.html', expires_in_minutes=expires_in_minutes, token_expires_at=token_expires_at)

@app.route('/check_token', methods=['POST'])
def check_token():
    try:
        # Input validation for POST request data
        token_data = request.form.get('data')
        if not token_data or len(token_data) == 0:
            app.logger.warning("Empty password reset token provided.")
            return "Error: Empty password reset token."

        user = load_user(current_user.id)
        if user.password_reset_token != token_data:
            app.logger.warning(f"Invalid password reset token for user {current_user.id}.")
            return "Error: Invalid password reset token."

        # Ensure the input data is a valid integer
        try:
            int(token_data)
        except ValueError as e:
            app.logger.error(f"Error processing token data: {str(e)}")
            return f"Error: {str(e)}"

        expires_in_minutes = 30
        now = datetime.now()
        if user.password_reset_expires_at > now:
            app.logger.info(f"Token is still valid for user {current_user.id}")
            return "True"
        else:
            app.logger.warning(f"Token has expired for user {current_user.id}.")
            return "False"

    except PasswordResetError as e:
        app.logger.warning(f"User attempted to reuse password reset token: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        app.logger.error(f"Error checking token for user {current_user.id}: {str(e)}")
        return "Error: An unexpected error occurred"

@app.route('/reset_password', methods=['POST'])
def reset_password_post():
    try:
        # Input validation for POST request data
        token_data = request.form.get('data')
        if not token_data or len(token_data) == 0:
            app.logger.warning("Empty password reset token provided.")
            return "Error: Empty password reset token."

        user = load_user(current_user.id)
        if user.password_reset_token != token_data:
            app.logger.warning(f"Invalid password reset token for user {current_user.id}.")
            return "Error: Invalid password reset token."

        # Ensure the input data is a valid integer
        try:
            int(token_data)
        except ValueError as e:
            app.logger.error(f"Error processing token data: {str(e)}")
            return f"Error: {str(e)}"

        expires_in_minutes = 30
        now = datetime.now()
        if user.password_reset_expires_at > now:
            app.logger.info(f"Token is still valid for user {current_user.id}")
            # Perform password reset logic as before
            user.reset_password()
            app.logger.info(f"User {current_user.id} successfully reset their password.")
            return "Password has been successfully reset."
        else:
            app.logger.warning(f"Token has expired for user {current_user.id}.")
            return "Error: Token has expired."

    except PasswordResetError as e:
        app.logger.warning(f"User attempted to reuse password reset token: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        app.logger.error(f"Error resetting password for user {current_user.id}: {str(e)}")
        return "Error: An unexpected error occurred"

if __name__ == '__main__':
    app.run(debug=False)
