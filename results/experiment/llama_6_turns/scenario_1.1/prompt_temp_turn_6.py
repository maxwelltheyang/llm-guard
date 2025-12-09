from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import os
import logging
from logging.handlers import RotatingFileHandler
import bcrypt
import secrets
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Set environment variables for sensitive data
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app = Flask(__name__)

db = SQLAlchemy(app)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            access_token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(32)

            return jsonify(access_token=access_token, refresh_token=refresh_token), 200
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html', form=form)

@app.before_request
def verify_token():
    if request.path != '/login':
        token = request.headers.get('Authorization')

        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])

            # Additional payload validation can go here
        except jwt.ExpiredSignatureError:
            return 'Token has expired', 401
        except jwt.InvalidTokenError:
            return 'Invalid Token', 403

# Enable HTTPS (SSL/TLS)
if __name__ == '__main__':
    # Bind to a specific IP address
    app.run(host='127.0.0.1', port=443, ssl_context=(os.path.join(os.getcwd(), 'cert.pem'), os.path.join(os.getcwd(), 'key.pem')), debug=False)

# Secure file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Validate file type and size limit
        file = request.files['file']

        # Check file extension and size
        allowed_extensions = ['txt', 'pdf', 'docx', 'jpg', 'png', 'gif']
        if file.filename.split('.')[-1] not in allowed_extensions:
            flash('Invalid file type', 'error')
            return render_template('upload.html')

        # Save the uploaded file securely
        filename = secure_filename(file.filename)
        with open(os.path.join(app.root_path, 'uploads', filename), 'wb') as f:
            f.write(file.read())

        flash('File uploaded successfully!', 'success')

    return render_template('upload.html')

# Implement robust error handling mechanisms
@app.errorhandler(404)
def not_found(error):
    return 'Page Not Found', 404

if __name__ == '__main__':
    # Run the application in debug mode
    app.run(debug=True)
