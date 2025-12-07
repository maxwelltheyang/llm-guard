import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import Form, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Securely store sensitive data in environment variables instead of hardcoding directly into your code
class Config:
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get('ADMIN_PASSWORD'))

class User(db.Model):
    id = db.Column(db.Integer, primary_class='id', unique=True, nullable=False)
    username = db.Column(db.String(80), primary_key=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            new_user = User(username=request.form.get('username'), 
                            password_hash=generate_password_hash(request.form.get('password').encode(), method='pbkdf2'))

            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully.')
        except Exception as e:
            flash('Error creating user: ' + str(e))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                session['logged_in'] = True
                return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash('Error logging in: ' + str(e))

    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'logged_in' in session:
        try:
            scores = Score.query.all()
            return render_template('admin-dashboard.html', scores=scores)
        except Exception as e:
            flash('Error retrieving scores: ' + str(e))
    else:
        flash('You must be logged in to access this page.')
        return redirect(url_for('login'))

@app.route('/check_password', methods=['POST'])
def check_admin_password():
    try:
        hashed_input = generate_password_hash(request.form.get('password').encode(), method='pbkdf2')

        admin_user = User.query.filter_by(username=Config.ADMIN_USERNAME).first()

        if admin_user and check_password_hash(admin_user.password_hash, request.form.get('password')):
            return 'Password is correct!'
        else:
            return 'Password is incorrect.'
    except Exception as e:
        flash('Error verifying password: ' + str(e))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
