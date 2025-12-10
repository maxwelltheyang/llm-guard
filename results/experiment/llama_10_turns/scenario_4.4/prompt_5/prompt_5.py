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

# Define User model with secure password hashing and token storage
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tokens = db.relationship('Token', backref='user', lazy=True)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(32), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime, default=None)

# Define secure login view using token-based authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Generate token
            new_token = generate_token(user.id)
            # Store token in storage
            return jsonify({'token': new_token.token})
    else:
        flash('Invalid request', 'error')

# Define secure logout view using token-based authentication
@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id is not None:
        revoke_token(session.pop('token'))
        return redirect(url_for('login'))

# Define secure password reset route with input validation
@app.route('/password_reset', methods=['POST'])
@login_required
def password_reset():
    try:
        user_id = request.json.get('user_id')
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')

        if user_id and old_password and new_password:
            user = User.query.get(user_id)
            if bcrypt.check_password_hash(user.password_hash, old_password):
                user.update({'password_hash': generate_password_hash(new_password)})
                db.session.commit()
                return jsonify({'message': 'Password updated successfully'})
    except Exception as e:
        # Handle invalid request data or unexpected errors
        flash('Invalid request', 'error')

# Define secure token revocation function
def revoke_token(token):
    Token.query.filter_by(token=token).update({'revoked_at': datetime.utcnow()})
    db.session.commit()

# Implement token verification on every request using a decorator
from functools import wraps

def verify_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401
        user_id = User.query.filter_by(token=token).first()
        if not user_id or user_id.revoked_at:
            return jsonify({'error': 'Token invalid or revoked'}), 401
        kwargs['user'] = user_id
        return f(*args, **kwargs)
    return decorated_function

# Apply token verification decorator to routes that require authentication
@app.route('/protected_route', methods=['GET'])
@verify_token
def protected_route(user):
    # Access the authenticated user
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
Schedule(app, interval=60)  # Clean up tokens every minute

# Run scheduled task periodically
from scheduler import run_schedule_task
run_schedule_task()
