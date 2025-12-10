import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtform_validations import validators

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_here'

# Set debug mode based on environment variable or configuration file
app.config['DEBUG'] = bool(os.environ.get('FLASK_DEBUG', '0'))

# Connect to the SQLite database
conn = sqlite3.connect('scores.db')
cursor = conn.cursor()

# Create a table for user scores if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER
    )
''')

# Create a table for admin login credentials if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
''')

# Load environment variables for secure storage of sensitive data
admin_username = os.environ.get('ADMIN_USERNAME')
admin_password = os.environ.get('ADMIN_PASSWORD')

if not cursor.fetchone():
    cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)",
                   (admin_username, admin_password))
    conn.commit()

# Initialize Flask-Login extension
login_manager = LoginManager()
login_manager.init_app(app)

class Admin(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(id):
    cursor.execute("SELECT * FROM admin WHERE id=?", (id,))
    return Admin(*cursor.fetchone())

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class UpdateScoreForm(FlaskForm):
    username = StringField('Username')
    score = IntegerField('Score')

@login_manager.user_loader
def load_user(id):
    cursor.execute("SELECT * FROM admin WHERE id=?", (id,))
    return Admin(*cursor.fetchone())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if the admin credentials are valid
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin_credentials = cursor.fetchone()

        if admin_credentials:
            user = load_user(admin_credentials[0])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html', form=form)

@app.route('/update_score', methods=['POST'])
def update_score():
    form = UpdateScoreForm()
    if form.validate_on_submit():
        if current_user.username == admin_username:
            cursor.execute("UPDATE scores SET score = ? WHERE username = ?", (form.score.data, form.username.data))
            conn.commit()

    return render_template('dashboard.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run()
