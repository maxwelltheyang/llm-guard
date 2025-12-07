import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import Form, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Load environment variables for secure configuration
if 'DATABASE_URI' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
else:
    # Use a default or local database URI as fallback (sqlite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'

# Load Flask debug setting from environment variable
if 'FLASK_DEBUG' not in os.environ:
    app.config['DEBUG'] = False

db = SQLAlchemy(app)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class User(db.Model):
    username = db.Column(db.String(64), primary_key=True)
    password_hash = db.Column(db.String(128))
    salt = db.Column(db.String(32))

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.InputRequired(), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        # Generate a random salt for the user's password
        import secrets
        salt = secrets.token_hex(16)

        # Hash the password with the generated salt
        password_hash = generate_password_hash(password, method='sha256')

        # Create a new user with the stored hash and salt
        new_user = User(username=username, password_hash=password_hash, salt=salt)
        db.session.add(new_user)
        db.session.commit()

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # TO DO: implement login logic here
    pass

@app.route('/admin/dashboard')
def admin_dashboard():
    scores = Score.query.all()
    return render_template('admin-dashboard.html', scores=scores)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config.get('DEBUG'))
