import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlite3 import Error as SqliteError, connect
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, email_validator, EqualTo, ValidationError
from flask_wtf.csrf import CSRFProtect
from bleach import clean
import secrets
from logging.config import dictConfig
import logging
import passlib.context

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },
                 'file': {
                     'class': 'logging.handlers.RotatingFileHandler',
                     'filename': 'app.log',
                     'maxBytes': 1024 * 1024 * 100,  # 100 MB
                     'backupCount': 10,
                     'formatter': 'default'
                 }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']
    }
})

app = Flask(__name__)
csrf = CSRFProtect(app)

# Generate a secret key for secure session management
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

# Secure session management using Flask-Session
from flask_session import Session
app.config["SESSION_PERMANENT"] = False  # Change this to True if you want the sessions to be stored in the database.
app.config["SESSION_TYPE"] = "filesystem"  # Use 'filesystem' for smaller apps or 'redis' for larger ones.

# Initialize session management
Session(app)

# Configure passlib context for password verification and hashing
pwd_context = passlib.context.CryptContext(
    schemes=["argon2"],
    default="argon2",
    bcrypt_rounds=12,
    # We do not need to specify any parameters here because we're using the default scheme.
)


def validate_password(password):
    """Validate a password"""
    if len(password) < 8:
        return False
    elif not any(char.isdigit() for char in password):
        return False
    elif not any(char.isupper() for char in password):
        return False
    else:
        return True


class RegistrationForm(FlaskForm):
    """Registration form"""
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), email_validator()])
    password = PasswordField("Password", validators=[DataRequired()])

    def validate_username(self, field):
        """Check if the username already exists in the database."""
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (field.data,))
        if cur.fetchone():
            raise ValidationError("Username is taken.")

    def validate_email(self, field):
        """Check if the email already exists in the database."""
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (field.data,))
        if cur.fetchone():
            raise ValidationError("Email is already in use.")


class PostForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])


def get_db():
    """Get the database object"""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(app.config["DATABASE"])
        return db


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Validate the password strength
        if not validate_password(password):
            flash("Password must be at least 8 characters long, contain a number and an uppercase letter.")
            return render_template("register.html", form=form)

        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password)))
        db.commit()

        # Clear the session
        session.clear()

    return render_template("register.html", form=form)


@app.route("/post", methods=["GET", "POST"])
def post():
    form = PostForm()
    if request.method == "POST":
        content = form.content.data

        # Validate the input data
        if len(content) < 1 or len(content) > 4096:
            flash("Content must be between 1 and 4096 characters.")
            return render_template("post.html", form=form)

        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO posts (content) VALUES (?)", (content,))
        db.commit()

        # Clear the session
        session.clear()

    return render_template("post.html", form=form)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    app.run(host=host, port=port)
