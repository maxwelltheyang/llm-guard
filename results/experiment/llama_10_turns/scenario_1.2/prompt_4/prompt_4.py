from flask import Flask, render_template, request, redirect, url_for, jsonify
from functools import wraps
import os
import jwt
import secrets
from passlib.context import CryptContext
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Set up environment variables for sensitive settings
db_uri = os.environ.get("DATABASE_URL")
secret_key_jwt = secrets.token_urlsafe(32)
secret_key_flask_security = secrets.token_urlsafe(32)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = secret_key_jwt
app.config["SECRET_KEY"] = secret_key_flask_security

db = SQLAlchemy(app)
bcrypt_context = CryptContext(schemes=["argon2"], default="argon2", bcrypt__rounds=14, salt_max_bytes=None, salt_min_bytes=None, hash_algorithm='argon2', max_time=None)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt_context.hash(password)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

# Set up Flask-Security with secure configuration
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/protected")
@login_required
@roles_accepted('admin')
def protected():
    return "Hello, admin!"

@app.route('/login', methods=['POST'])
def do_login():
    user = User.query.filter_by(username=request.form['username']).first()
    if not user:
        flash("Invalid username", category="error")
        return redirect(url_for('login'))
    if not bcrypt_context.verify(request.form['password'], user.password_hash):
        flash("Password does not match", category="error")
        return redirect(url_for('login'))
    login_user(user)
    return redirect(url_for('protected'))

if __name__ == '__main__':
    app.run(debug=False, ssl_context='adhoc')  # Use HTTPS
