import os
from flask import Flask, session, redirect, url_for, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()  # Load environment variables from a .env file

# Secret Key Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Database URI Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(app)

# Model Definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# View Functions
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return f"Hello, {user.username}!"
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# Add Content-Security-Policy, X-Frame-Options, and X-Content-Type-Options headers for enhanced security
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Ensure debug is disabled in production
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True if os.getenv('FLASK_ENV') != 'production' else False)
