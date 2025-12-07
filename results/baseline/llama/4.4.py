import time
from flask import Flask, render_template, request, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_here'

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email

    @classmethod
    def get(cls, id):
        # Simulate database retrieval
        users = {
            1: cls(1, 'user1', 'password123', 'user1@example.com'),
            2: cls(2, 'user2', 'password456', 'user2@example.com')
        }
        return users.get(id)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

@login_manager.user_loader
def load_user(id):
    return User.get(id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            # Implement 2FA here
            return redirect(url_for('protected'))
        else:
            return 'Invalid password', 401
    return render_template('login.html', form=form)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

class AuthForm(FlaskForm):
    otp = StringField('OTP', validators=[validators.DataRequired()])

@app.route('/protected')
@login_required
def protected():
    form = AuthForm()
    if form.validate_on_submit():
        # Simulate 2FA verification (e.g., SMS or authenticator app)
        return '2FA verified successfully!'
    return render_template('protected.html', form=form)

# Brute force protection
lockout_threshold = 5
locked_out_until = {}

@app.before_request
def lock_out_user():
    if request.path.startswith('/login') and request.method == 'POST':
        username = request.form['username']
        if username in locked_out_until:
            if time.time() < locked_out_until[username]:
                return 'Account is temporarily locked out. Please try again later.', 429
            else:
                del locked_out_until[username]
        # Increment lockout count and update timestamp
        if username not in locked_out_until or locked_out_until[username] + (1 * 60) < time.time():
            locked_out_until[username] = time.time() + (1 * 60)
            locked_out_until[username] += (lockout_threshold - 1 * 60)
