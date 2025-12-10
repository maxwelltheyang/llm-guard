from flask import Flask, render_template, request, current_app, redirect, url_for, flash, abort
import os
import logging
from argon2 import PasswordHasher
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Load database URL from environment variable or default to None
db_url = os.getenv('DATABASE_URL', 'sqlite:///database.db')

try:
    engine = create_engine(db_url)
except SQLAlchemyError as e:
    print(f'Failed to connect to the database: {e}')
    flash('Database connection error occurred. Please check your database configuration.', 'error')
    exit(1)

Base = automap_base()

Base.prepare(engine, reflect=True)

# Verify hash format stored in the database
def verify_hash_format(hashed_password):
    # Argon2 hashes are around 60 characters long (depending on configuration)
    return len(hashed_password) > 50

# Re-hash existing user passwords
@app.route('/rehash_passwords')
def rehash_passwords():
    try:
        with Session() as session:
            users = User.query.all()

            for user in users:
                try:
                    hashed_password = ph.hash(user.password_hashed)

                    if verify_hash_format(hashed_password):
                        # Update the existing password hash
                        user.password_hashed = hashed_password
                        session.commit()

                    else:
                        print(f'Invalid hash format: {hashed_password}')

                except SQLAlchemyError as e:
                    # Handle database errors
                    print(f'Database error: {e}')
                    flash('Database error occurred during password re-hashing', 'error')

    except Exception as e:
        # Handle generic exceptions
        print(f'An unexpected issue occurred: {e}')
        flash('An unexpected issue occurred while processing user passwords', 'error')

    return redirect(url_for('index'))

# Validate user inputs against expected formats and lengths before passing them to database operations or other security-sensitive areas.
def validate_username(username):
    # Check if the username is at least 3 characters long
    return len(username) >= 3

@app.route('/')
def index():
    try:
        with Session() as session:
            users = session.query(User).all()

            for user in users:
                if not validate_username(user.username):
                    print(f'Invalid username: {user.username}')

    except Exception as e:
        # Handle generic exceptions
        print(f'An unexpected issue occurred: {e}')
        flash('An unexpected issue occurred while retrieving user data', 'error')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
