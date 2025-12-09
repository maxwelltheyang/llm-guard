from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
import os

# Define a default SECRET_KEY in case it's not set as an environment variable
app.config['SECRET_KEY'] = 'default-secret-key'

# Load environment variables for the application configuration
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Enable HTTPS for session security
app.config['SESSION_COOKIE_SECURE'] = True

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

# Define a custom module for password validation using Django's password_validation app
from django.contrib.auth.password_validation import validate_password

class RegistrationForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$",
                          message="Password should contain at least 1 uppercase letter, "
                                  "1 lowercase letter, 1 digit and special character.")
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data)
            # Validate password
            validate_password(form.password.data, user.__dict__)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Password does not meet the requirements: {e}')
    return render_template('register.html', form=form)

if __name__ == '__main__':
    # Disable debug mode for production security
    app.run(debug=False)
