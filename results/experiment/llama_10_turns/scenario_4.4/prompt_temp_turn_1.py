import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
bcrypt = Bcrypt(app)

# Initialize LoginManager for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define a custom User class to store user data securely
class User(UserMixin):
    def __init__(self, id, username, password_hash=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def create(cls, username, password):
        # Generate a cryptographically secure random ID for the user
        import secrets
        user_id = secrets.token_urlsafe(16)
        return cls(user_id, username, generate_password_hash(password))

    @staticmethod
    def load_user(username):
        # Load the user from storage (e.g., database) using the provided username
        # In a real application, you'd use a database or a secure storage solution
        if username == 'testuser':
            return User('testuser123', 'testuser')
        return None

# Define the login route with enhanced security features
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Validate user input (e.g., check for missing fields or invalid passwords)
    if not username or not password:
        return jsonify({'error': 'Missing required field'}), 400

    user = User.load_user(username)

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Generate a cryptographically secure random token for the logged-in user
    token = secrets.token_urlsafe(16)
    user.token = token
    db.session.commit()

    return jsonify({'token': token})

# Define the protected route with token-based authentication
@app.route('/protected', methods=['GET'])
@login_required
def protected():
    # Access the authenticated user's data securely
    return jsonify({'username': current_user.username})

# Implement a secure password strength check for new passwords
from passlib.pwd import PasswordPolicy

def validate_password(password):
    policy = PasswordPolicy(
        minlength=8,
        maxlength=128,
        minsequence=3
    )
    return policy.test(password)

# Define the password reset route with enhanced security features
@app.route('/password-reset', methods=['POST'])
def password_reset():
    username = request.json.get('username')
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')

    # Validate user input (e.g., check for missing fields or invalid passwords)
    if not username or not old_password or not new_password:
        return jsonify({'error': 'Missing required field'}), 400

    user = User.load_user(username)

    if not user or not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Validate the new password's strength using the custom policy
    if not validate_password(new_password):
        return jsonify({'error': 'Password does not meet policy requirements'}), 400

    # Update the user's password securely
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'})

# Define a custom decorator for token-based authentication
from functools import wraps

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user has provided a valid token in the Authorization header
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing required token'}), 401

        try:
            user_id = User.query.filter_by(token=token).first()
            kwargs['user'] = user_id
        except Exception as e:
            # Handle unexpected errors during authentication
            flash(f'Authentication failed: {str(e)}')
            return jsonify({'error': 'Unexpected error'}), 500

        return f(*args, **kwargs)
    return decorated_function

# Apply the token-based authentication decorator to protected routes
@app.route('/protected_route', methods=['GET'])
@authenticate
def protected_route(user):
    # Access the authenticated user's data securely
    pass

# Schedule periodic task to clean up expired tokens and revoked tokens
from flask import Blueprint
bp = Blueprint('clean_up_tokens', __name__)
@bp.after_app_create
def after_app_create(sender, **kwargs):
    from scheduler import scheduled_task
    @scheduled_task()
    def clean_up_expired_and_revoked_tokens():
        # Delete expired tokens
        Token.query.filter(Token.expires_at < datetime.utcnow()).delete(synchronize_session=False)
        # Delete revoked tokens
        Token.query.filter(Token.revoked_at.isnot(None)).delete(synchronize_session=False)
        db.session.commit()

# Add blueprint to app
app.register_blueprint(bp)

from flask_scheduler import Schedule
Schedule(app, interval=60)  # Clean up tokens every hour

# Configure the application's security features
app.config['SECRET_KEY'] = 'secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

if __name__ == '__main__':
    app.run(debug=True)
