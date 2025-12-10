import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe
import logging

# Initialize Flask app
app = Flask(__name__)

# Load configuration from environment variables or default values
if 'SECRET_KEY' not in os.environ:
    raise ValueError("SECRET_KEY environment variable is not set")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Properly set the DEBUG flag based on the FLASK_DEBUG environment variable
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG') == 'True'

# Initialize logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
logger.info("Using production settings to ensure maximum security")

# Initialize scheduled tasks with a fixed schedule (every hour)
from scheduler import scheduled_task
@scheduled_task()
def clean_up_expired_and_revoked_tokens():
    # Delete expired tokens, using the database timezone for accurate cleanup
    Token.query.filter(Token.expires_at < db.func.now()).delete(synchronize_session=False)
    # Delete revoked tokens
    Token.query.filter(Token.revoked_at.isnot(None)).delete(synchronize_session=False)
    db.session.commit()

# Initialize custom error handlers for exception handling and logging
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"Error 404: {e}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Error 500: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run Flask with production settings
    app.run()
