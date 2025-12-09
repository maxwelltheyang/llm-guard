from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))  # Load environment variables from .env file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'scores.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # Initialize Bcrypt for password hashing

# Load allowed user IDs from database table (example)
class AllowedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')  # Validate and sanitize form data
    password = request.form.get('password')

    if not username or not password:  # Check if both fields are present and not empty
        flash('Please fill in all fields', category='error')
        return render_template('register.html')

    user = User.query.filter_by(username=username).first()
    if user:
        flash('Username already exists', category='error')
        return render_template('register.html')

    try:
        new_user = User(username=username, password_hash=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"Error registering user: {str(e)}", category='error')
        return render_template('register.html')

@app.route('/update_score', methods=['POST'])
def update_score():
    user_id = request.form.get('user_id')  # Validate and sanitize form data
    if not user_id:  # Check if field is present and not empty
        flash('Invalid user ID', category='error')
        return render_template('dashboard.html')

    allowed_user_ids = [user.user_id for user in db.session.query(AllowedUser).all()]  # Load whitelisted IDs from database
    if user_id not in allowed_user_ids:
        flash('Access denied for this user ID', category='error')
        return render_template('dashboard.html')

    new_score = request.form.get('score')  # Validate and sanitize score
    try:
        new_score = float(new_score)
    except ValueError:
        flash('Invalid score', category='error')
        return render_template('dashboard.html')

    score_to_update = Score.query.filter_by(user_id=user_id).first()
    if score_to_update:
        score_to_update.score = new_score
        db.session.commit()

        flash('Score updated successfully.', category='success')
        return render_template('dashboard.html')
    else:
        flash('No score found for this user ID', category='error')
        return render_template('dashboard.html')

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        flash(f"Error initializing database: {str(e)}", category='error')
    finally:
        app.run(debug=False)  # Set debug to False for production
