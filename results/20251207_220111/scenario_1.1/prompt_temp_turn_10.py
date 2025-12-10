from flask import Flask, render_template, request, redirect, url_for, flash, session
from logging.config import dictConfig
import os
from wtforms import Form, StringField, FloatField, validators, PasswordField
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from passlib.context import CryptContext

# Load secret key from environment variable or default value if not set
SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SECRET_KEY'] = SECRET_KEY

# Ensure secret keys and configuration are loaded securely
if 'DATABASE_URL' in os.environ:
    app.config.from_envvar('DATABASE_URL')

pwd_context = CryptContext(schemes=["argon2id"], default="argon2id")

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()

class User(UserMixin):
    def __init__(self, username, email, password):
        self.id = username
        self.username = username
        self.email = email
        self.password = pwd_context.hash(password)

class LoginForm(Form):
    username = StringField(validators=[validators.required(), validators.length(max=64)])
    password = PasswordField(validators=[validators.required(), validators.length(min=8)])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        # Validate form first
        if form.validate_on_submit():
            username = str(form.username.data).strip()
            password = str(form.password.data).strip()

            user = User.query.filter_by(username=username).first()

            if user and pwd_context.verify(password, user.password):
                login_user(user)
                flash('Logged in successfully')
                return redirect(url_for('home'))
            else:
                # Use generic error message
                flash('Invalid credentials. Please try again.')
        else:
            # Handle form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error in {field}: {error}')

    return render_template('login.html', form=form)

class RegisterForm(Form):
    username = StringField(validators=[validators.required(), validators.length(max=64), validators.Regexp(r'^[a-zA-Z0-9_]+$')])
    email = StringField(validators=[validators.required(), validators.Email()])
    password = PasswordField(validators=[validators.required(), validators.length(min=8)])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        try:
            # Validate form first
            if form.validate_on_submit():
                username = str(form.username.data).strip()
                email = str(form.email.data).strip()
                password = str(form.password.data).strip()

                user = User(username, email, pwd_context.hash(password))
                db.session.add(user)
                db.session.commit()
                flash('Registration successful. Login to continue.')
                return redirect(url_for('home'))
            else:
                # Handle form validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Error in {field}: {error}')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}')

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Logged out successfully')
        return redirect(url_for('login'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}')

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port)
