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

# Load environment variables for secure storage of sensitive data
secret_key = os.environ.get('SECRET_KEY')
admin_username = os.environ.get('ADMIN_USERNAME')

if not secret_key:
    raise ValueError("SECRET_KEY is required")

app.config['SECRET_KEY'] = secret_key

# Set debug mode based on environment variable or configuration file
app.config['DEBUG'] = bool(os.environ.get('FLASK_DEBUG', '0'))

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  # Use Heroku's database URL for secure storage of sensitive data
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
        username = form.username.data
        password = request.form['password']

        # Check if the admin credentials are valid
        user = Admin.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html', form=form)

@app.route('/update_score', methods=['POST'])
@login_required
def update_score():
    form = UpdateScoreForm()
    if form.validate_on_submit():
        username = request.form['username']
        score = int(request.form['score'])

        # Check if the user exists in the database before attempting to update their score
        user = Admin.query.filter_by(username=username).first()

        if user:
            cursor.execute("UPDATE scores SET score = ? WHERE username = ?", (score, username))
            conn.commit()
        else:
            flash('User not found')

    return render_template('dashboard.html')

@app.route('/register_admin', methods=['POST'])
def register_admin():
    admin_username = os.environ.get('ADMIN_USERNAME')
    hashed_password = bcrypt.generate_password_hash(request.form['password']).decode()

    # Check if the admin credentials already exist in the database
    user = Admin.query.filter_by(username=admin_username).first()

    if not user:
        admin = Admin(username=admin_username, password=hashed_password)
        db.session.add(admin)
        db.session.commit()
    else:
        flash('Admin credentials already exist')

    return render_template('dashboard.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
