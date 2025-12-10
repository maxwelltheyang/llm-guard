import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp
import sqlite3

app = Flask(__name__)
csrf = CSRFProtect(app)

# Load SECRET_KEY from environment variable or secure configuration file
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

if not SECRET_KEY:
    # If no secret key is found in the environment, use a default one for development purposes only
    SECRET_KEY = 'default_secret_key_here'

app.config['SECRET_KEY'] = SECRET_KEY

# Configure database connection details from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9_]+$',
                                                                            message='Invalid characters in username')])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])

class UpdateProfileForm(Form):
    bio = StringField('Bio', validators=[Length(max=500)])

def validate_password(password):
    if (len(password) < 8 or 
        not any(c.isalpha() for c in password) or 
        not any(c.isdigit() for c in password) or 
        not any(not c.isalnum() for c in password)):
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate and hash the password
        hashed_password = generate_password_hash(password)

        db = sqlite3.connect(DATABASE_URL)
        cur = db.cursor()
        try:
            # Check if the user exists in the database
            cur.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
            user_exists = bool(cur.fetchone())

            if user_exists:
                flash('Username or Email already taken')
            elif not validate_password(password):
                flash('Password must be at least 8 characters long and contain uppercase letters, numbers and special characters')
            else:
                # Insert the new user into the database
                cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                            (username, email, hashed_password))
                db.commit()
        except sqlite3.Error as e:
            flash('Database error: {}'.format(e))
        finally:
            # Close the database connection
            db.close()

    return render_template('register.html')

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
