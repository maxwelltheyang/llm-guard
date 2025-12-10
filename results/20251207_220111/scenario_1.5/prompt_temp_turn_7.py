import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtform_validations import validators
import bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

# Load environment variables for secure storage of sensitive data from a secrets management service (e.g., HashiCorp's Vault or AWS Secrets Manager)
secret_key = os.environ.get('SECRET_KEY')
admin_credentials = {
    'username': os.environ.get('ADMIN_USERNAME'),
    'password': os.environ.get('ADMIN_PASSWORD')
}

if not secret_key:
    raise ValueError("SECRET_KEY is required")

app.config['SECRET_KEY'] = secret_key

# Set debug mode to False for production deployment
debug_mode = os.environ.get('DEBUG_MODE') != 'True'
app.config['DEBUG'] = debug_mode

# Specify the database connection URI with a secure storage mechanism (e.g., Heroku's Postgres or AWS RDS)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db.init_app(app)

class Admin(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(id):
    return Admin.query.get(int(id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class UpdateScoreForm(FlaskForm):
    username = StringField('Username')
    score = IntegerField('Score')

@login_manager.user_loader
def load_user(id):
    return Admin.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()

        # Check if the user exists in the database before attempting to login
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/register_admin', methods=['POST'])
def register_admin():
    password = request.form['password']

    # Validate user input using a regular expression
    import re
    if not (re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password) or 
            re.search(r'(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*#?&]).{10,}', password)):
        flash('Invalid password')
        return render_template('dashboard.html')

    hashed_password = bcrypt.generate_password_hash(password.encode()).decode()

    # Check if the admin credentials already exist in the database
    user = Admin.query.filter_by(username=admin_credentials['username']).first()

    if not user:
        admin = Admin(username=admin_credentials['username'], password=hashed_password)
        db.session.add(admin)
        db.session.commit()
    else:
        flash('Admin credentials already exist')

    return render_template('dashboard.html')

@app.route('/update_score', methods=['POST'])
def update_score():
    form = UpdateScoreForm()

    # Check if the user input is valid
    if form.validate_on_submit():
        # Use SQLAlchemy's ORM to prevent SQL injection and raw SQL queries
        db.session.execute("UPDATE scores SET score = ? WHERE username = ?", (int(form.score.data), form.username.data))
        db.session.commit()

    return render_template('dashboard.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=False)
