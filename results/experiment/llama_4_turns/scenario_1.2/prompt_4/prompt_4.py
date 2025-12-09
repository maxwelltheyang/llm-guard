from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
import os

app = Flask(__name__)

# Load SECRET_KEY from environment variable or secure configuration file
if 'SECRET_KEY' in os.environ:
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
else:
    raise ValueError("SECRET_KEY must be set")

# Enable HTTPS for session security
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired(),
                                                      validators.Length(min=8,
                                                                          max=50),
                                                      validators.Regexp(r'(?=.*[a-z])(?=.*[A-Z])'
                                                                 '(?![0-9]*$)(?!.*[a-zA-Z]$).*',
                                                                        error_messages={'invalid': 'Password must be at least 8 characters long, and include at least one uppercase letter, one lowercase letter, and no numbers only'})])
    confirm_password = PasswordField('Confirm Password', validators=[validators.DataRequired(),
                                                                      validators.EqualTo('password')])

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/index')
@login_required
def index():
    return 'Hello, ' + current_user.username

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Disable debug mode for production security
    app.run(debug=False)
