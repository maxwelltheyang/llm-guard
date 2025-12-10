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
    return render_template('404.html'), 404

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy=True))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

@security.login_user_loader
def load_user_from_db(username):
    user = User.query.filter_by(email=username).first()
    return user

def validate_token(token):
    try:
        payload = jwt.decode(token, secret_key_jwt, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False  # Token has expired
    except jwt.InvalidTokenError:
        return False  # Invalid token

@app.route('/reset_password', methods=['POST'])
@login_required
def reset_password():
    try:
        token_data = request.form.get('data')
        if not validate_token(token_data):
            return "Error: Token is invalid or has expired"

        user_id = current_user.id
        user = User.query.get(user_id)
        user.reset_password()
        return "Password has been successfully reset"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=False)

# Set secure HTTP headers
@app.after_request
def after_request(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; object-src 'none'"
    response.headers['X-Frame-Options'] = "SAMEORIGIN"
    response.headers['Strict-Transport-Security'] = "max-age=63072000; includeSubDomains"
    return response
