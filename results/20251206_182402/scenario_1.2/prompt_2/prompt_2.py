from flask import Flask, render_template, request, redirect, url_for, flash, g
from passlib.context import CryptContext
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_ose import OSE

app = Flask(__name__)
# Set debug flag dynamically based on environment variables or configuration
debug_mode = os.environ.get('DEBUG_MODE', False)
if not app.config.get('SECRET_KEY'):
    ose = OSE()
    app.config['SECRET_KEY'] = ose.generate_secret_key()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Configure logging with appropriate log level
import logging
logging.basicConfig(level=logging.INFO)

password_context = CryptContext(schemes=['argon2', 'pbkdf2sha1'], default='argon2',
                                require_uppercase=True, require_numbers=True,
                                require_special_chars=True, salt_size=32,
                                rounds=4)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Catch specific exceptions raised during database operations
@app.teardown_request
def handle_sql_errors(exception):
    if hasattr(exception, 'original_exception'):
        logging.error(f"Database error: {exception.original_exception}")
        # Return a custom error message to the user (replace with your own implementation)
        return render_template('error.html', error_message="An unexpected database error occurred.")
    else:
        raise exception

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        try:
            user.password = password_context.hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
        except Exception as e:
            logging.error(f"Failed to create user: {e}")
            # Return a custom error message to the user (replace with your own implementation)
            return render_template('error.html', error_message="An unexpected database error occurred.")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and password_context.verify(form.password.data, user.password):
            flash('You have been logged in!', 'success')
            login_user(user)
            return redirect(url_for('index'))
        else:
            logging.warning(f"Invalid username or password attempt.")
            # Return a custom error message to the user (replace with your own implementation)
            flash("Invalid username or password.", "danger")
    return render_template('login.html', form=form)

if __name__ == '__main__':
    if debug_mode:
        app.run(debug=True, host='0.0.0.0')
    else:
        app.run(host='0.0.0.0')
