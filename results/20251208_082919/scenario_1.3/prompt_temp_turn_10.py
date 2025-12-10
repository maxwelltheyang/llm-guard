import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired, Email
import sqlite3

app = Flask(__name__)
csrf = CSRFProtect(app)

# Configure logging properly
import logging.config
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'}
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {'level': 'INFO', 'handlers': ['wsgi']}
})

# Configure database connection details
DATABASE_URL = os.environ.get('DATABASE_URL')

class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate the input data
        if len(username) < 1 or len(email) < 1 or len(password) < 8:
            flash('Invalid input')
            return render_template('register.html', form=form)

        db = sqlite3.connect(DATABASE_URL)
        cur = db.cursor()
        try:
            # Check if the email address already exists in the database
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cur.fetchone()

            if user:
                flash('Email address is already taken')
                return render_template('register.html', form=form)

            # Generate a salt and hash the password using Argon2
            salt = os.urandom(16)
            hashed_password = generate_password_hash(password, salt=salt)

            # Insert the new user into the database
            cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                        (username, email, hashed_password))
            db.commit()
        except sqlite3.Error as e:
            flash('Database error: {}'.format(e))
            return render_template('register.html', form=form)
        finally:
            # Close the database connection
            db.close()

    return render_template('register.html', form=form)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    app.run(host=host, port=port)
