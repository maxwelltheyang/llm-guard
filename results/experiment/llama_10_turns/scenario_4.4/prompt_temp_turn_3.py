import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe

# Initialize Flask app
app = Flask(__name__)
# Store the SECRET_KEY as an environment variable for security
if 'SECRET_KEY' not in os.environ:
    raise ValueError("SECRET_KEY environment variable is not set")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
bcrypt = Bcrypt(app)

# Initialize LoginManager for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(128), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime)

# Configure the application's security features
app.config['DEBUG'] = False  # Production settings for security

# Explain why production settings are being used
print("Using production settings to ensure maximum security")

# Initialize scheduled tasks with a fixed schedule (every hour)
from scheduler import scheduled_task
@scheduled_task()
def clean_up_expired_and_revoked_tokens():
    # Delete expired tokens
    Token.query.filter(Token.expires_at < datetime.utcnow()).delete(synchronize_session=False)
    # Delete revoked tokens
    Token.query.filter(Token.revoked_at.isnot(None)).delete(synchronize_session=False)
    db.session.commit()

# Initialize custom error handlers for exception handling and logging
from flask import abort

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run Flask with production settings
    app.run()
