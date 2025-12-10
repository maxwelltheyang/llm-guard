import logging.config
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

# Set up logging configuration to write logs to a file
logging.config.dictConfig({
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
            'level': 'ERROR',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'level': 'INFO'
        }
    },
    'root': {
        'handlers': ['wsgi', 'file']
    }
})

from wtforms.validators import ValidationError

class User(UserMixin, object):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def validate_password(password):
        try:
            # Password validation for educational institute's students
            if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
                raise ValidationError('Password must be at least 8 characters long, contain at least one digit and one letter.')
        except Exception as e:
            raise ValidationError(f"Password validation failed: {e}")

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

app = Flask(__name__)
login_manager = LoginManager(app)

# Define database connection
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class UserTable(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password_hash = Column(String)

# Create table in database
engine = create_engine('sqlite:///example.db')
Base.metadata.create_all(engine)

@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(None, form.username.data, None)
        validate_password(form.password.data)  # Validate the password here
        new_user.set_password(form.password.data)
        with engine.connect() as connection:
            result = connection.execute("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)", 
                                        {'username': new_user.username, 'password_hash': new_user.password_hash})
        return redirect(url_for('login'))
    else:
        flash('Error registering user', 'error')
        return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(debug=False)
