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

bcrypt_context = CryptContext(schemes=["argon2"], default="argon2", bcrypt__rounds=14, argon2__salt_max_bytes=32, argon2__salt_min_bytes=16)

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

    def reset_password(self):
        self.last_password_reset = datetime.now()

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
            app.logger.warning("No user found with the given ID.")
        elif isinstance(e, TypeError):
            app.logger.error("Invalid ID type. Expected integer.")
        else:
            app.logger.error(f"Unexpected error: {str(e)}")
        return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return 'Hello, authenticated user!'
    else:
        return 'Hello, anonymous!'

@app.route('/reset_password', methods=['POST'])
@login_required
def reset_password():
    user = load_user(current_user.id)
    if user.last_password_reset and (datetime.now() - user.last_password_reset).total_seconds() < 3600:
        app.logger.warning("User attempted to reuse password reset token.")
        return "Error: Password reset token has been reused."
    try:
        user.reset_password()
        db.session.commit()
        app.logger.info(f"User {current_user.id} successfully reset their password.")
        return "Password has been successfully reset."
    except Exception as e:
        app.logger.error(f"Error resetting password for user {current_user.id}: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=False)
