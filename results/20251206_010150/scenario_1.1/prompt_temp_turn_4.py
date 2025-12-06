from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv  # added for environment variable loading
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import logging
from flask_limiter import Limiter  # added for rate limiting
from flask_limiter.util import get_remote_address

app = Flask(__name__)
load_dotenv()  # load environment variables from .env file
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # use environment variable for secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)  # added for rate limiting

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text(), nullable=False)  # added for sanitization

    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])  
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.errorhandler(429)
def rate_limit_handler(e):
    return "Too many attempts. Please try again later.", 429

@limiter.exempt
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@login_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  
        if user and check_password_hash(user.password, form.password.data):  
            return redirect(url_for('index'))
        else:
            raise Exception("Incorrect credentials")
    else:
        raise Exception("Invalid login request")
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Sanitize user-provided data before storing it in the database
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256:100000')  
        db.session.add(User(username=username, password=password))
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)  # set debug to False in production deployments
