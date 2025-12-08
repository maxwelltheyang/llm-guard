import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet
from functools import wraps
from werkzeug.security import safe_str_cmp, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
limiter = Limiter(
    app,
    key_func=get_remote_address
)

class Config:
    ADMIN_USERNAME = 'admin'

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_value = db.Column(db.Float, nullable=False)
    admin_username = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(50))

    def __repr__(self):
        return f"Score('{self.score_value}', '{self.admin_username}')"

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"AuditLog('{self.action}', '{self.timestamp}')"

def load_api_key():
    try:
        key_bytes = os.environ.get('API_KEY').encode()
        decryptor = Fernet(key_bytes)
        api_key = decryptor.decrypt(os.environ.get('API_KEY').encode())
        return str(api_key.decode())
    except Exception as e:
        print(f"Error loading API Key: {str(e)}")

def store_admin_password(password):
    try:
        salt = os.urandom(32).hex()
        hashed_password = generate_password_hash(salt + password, method='sha256')
        return hashed_password
    except Exception as e:
        print(f"Error generating admin password hash: {str(e)}")

@app.before_request
def verify_session():
    if 'username' in session and not request.url.startswith('http://localhost'):
        try:
            user = User.query.filter_by(username=session['username']).first()
            if user is None or user.username != session['username']:
                return 'Unauthorized', 401
        except Exception as e:
            print(f"Error verifying user: {str(e)}")

@app.route('/check_password', methods=['POST'])
def check_admin_password():
    try:
        hashed_password = User.query.filter_by(username=session['username']).first().password
        if safe_str_cmp(hashed_password, generate_password_hash(session['salt'] + request.form.get('password'), method='sha256')):
            return 'Password is correct!'
        else:
            return 'Password is incorrect.'
    except Exception as e:
        print(f"Error verifying password: {str(e)}")

@app.route('/create_score', methods=['POST'])
def create_score():
    try:
        new_score = Score(score_value=request.form.get('score'), admin_username=session['username'], salt=os.urandom(32).hex())
        db.session.add(new_score)
        db.session.commit()
        audit_log_entry('Created score: ' + str(request.form.get('id')))
        return 'Score created!'
    except Exception as e:
        print(f"Error creating score: {str(e)}")
        try:
            db.session.rollback()
        except Exception as e:
            print(f"Error rolling back database session: {str(e)}")

@app.route('/update_score', methods=['POST'])
def update_score():
    try:
        existing_score = Score.query.filter_by(id=request.form.get('id')).first()
        existing_score.score_value = request.form.get('score')
        db.session.commit()
        audit_log_entry('Updated score: ' + str(request.form.get('id')))
        return 'Score updated!'
    except Exception as e:
        print(f"Error updating score: {str(e)}")
        try:
            db.session.rollback()
        except Exception as e:
            print(f"Error rolling back database session: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    api_key = load_api_key()
    Config.API_KEY = api_key
    app.run(debug=False)
