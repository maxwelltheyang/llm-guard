import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp
import sqlite3

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'secret_key_here'

# Configure database connection details from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9_]+$',
                                                                            message='Invalid characters in username')])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])

class UpdateProfileForm(Form):
    bio = StringField('Bio', validators=[Length(max=500)])

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

@app.route('/update-profile', methods=['GET', 'POST'])
def update_profile():
    if not session.get('username'):
        return redirect(url_for('login'))

    username = session['username']
    user_bio = ''

    db = sqlite3.connect(DATABASE_URL)
    cur = db.cursor()
    try:
        # Retrieve the bio of the current user
        cur.execute("SELECT bio FROM users WHERE username=?", (username,))
        user_bio = cur.fetchone()[0]
    except sqlite3.Error as e:
        flash('Database error: {}'.format(e))
    finally:
        # Close the database connection
        db.close()

    form = UpdateProfileForm()

    if request.method == 'POST':
        bio = request.form['bio']

        # Validate and update user bio
        try:
            cur.execute("UPDATE users SET bio=? WHERE username=?", (bio, username))
            db.commit()
        except sqlite3.Error as e:
            flash('Database error: {}'.format(e))

    return render_template('update-profile.html', form=form, user_bio=user_bio)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000

    app.run(host=host, port=port)
