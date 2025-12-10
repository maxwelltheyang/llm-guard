from flask import Flask, render_template, request, redirect, url_for, flash
from logging.config import dictConfig
import os
from wtforms import Form, StringField, FloatField, validators, PasswordField
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# Set up logging configuration
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_logger',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
else:
    logging.error("SECRET_KEY not set. Aborting startup.")
    raise RuntimeError('SECRET_KEY must be set')

app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', False)

# Update SQLALCHEMY_ECHO configuration to use environment variable
if os.environ.get('SQLALCHEMY_ECHO') and app.config['DEBUG']:
    app.config['SQLALCHEMY_ECHO'] = True

# Set up production-specific configurations only if the correct env is set
if 'PROD_MODE' in os.environ and os.environ['PROD_MODE'] == 'True':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', None)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["argon2"], default="argon2")

            # This will hash the password
            hashed_password = pwd_context.hash(password)
            self.password_hash = hashed_password

        except ImportError:
            logging.error("Failed to update password hashing algorithm. Using deprecated method.")
            try:
                validate_password(password)
            except ValueError as e:
                logging.error(f"Invalid password: {e}")
                return  # Abort setting the password if it's invalid
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["argon2"], default="argon2")

            # This will verify that the provided password is correct
            return pwd_context.verify(password, self.password_hash)

        except ImportError:
            logging.error("Failed to update password hashing algorithm. Using deprecated method.")
            try:
                validate_password(password)
            except ValueError as e:
                logging.error(f"Invalid password: {e}")
                return False  # If the provided password is invalid
            return check_password_hash(self.password_hash, password)

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('User created successfully')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully')
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully')
    return redirect(url_for('login'))

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)
