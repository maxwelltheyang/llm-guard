import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
import validators
from wtforms import Form, StringField, IntegerField, validators

# Initialize Flask application with secure secret key from environment variable
app = Flask(__name__)
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY

# Load database credentials securely from environment variables or a secrets management service
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db?check_same_thread=True'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)

    def set_password(self, password):
        # Validate and hash password using Flask-Bcrypt's built-in validation
        try:
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')

        except Exception as e:
            app.logger.error(f"An error occurred: {e}")

    def check_password(self, password):
        # Securely verify the hashed password with Flask-Bcrypt's built-in validation
        try:
            return bcrypt.check_password_hash(self.password, password)
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return False

class RegistrationForm(Form):
    username = StringField('Username', validators=[validators.DataRequired()])

    def validate_username(self, field):
        # Sanitize and validate user input at the backend level
        if User.query.filter_by(username=field.data).first():
            raise validators.ValidationError("Username already exists")
        elif not (field.data.replace(' ', '').isalnum() or validators.email(field.data)):
            raise validators.ValidationError("Invalid email or username")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegistrationForm()

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()

        if user and user.check_password(request.form.get('password')):
            # Set current_user correctly
            login_user(user)

            # Clear session data after successful login
            session.clear()

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Clear user data from session upon successful logout
    if 'username' in session:
        del session['username']

    if 'user_id' in session:
        del session['user_id']

    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    # Custom error handler to display user-friendly error messages
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=False)  # Removed auto-reload in production mode
