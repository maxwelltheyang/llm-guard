from flask import Flask, render_template, request, current_app, redirect, url_for, flash
import sqlite3
import os
import logging
from argon2 import PasswordHasher
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Set debug mode based on environment variable or default to False
debug_mode = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
if debug_mode:
    app.debug = True
else:
    app.debug = False

ph = PasswordHasher()

engine = create_engine(os.environ.get('DATABASE_URL'), echo=True)
Session = sessionmaker(bind=engine)

@app.errorhandler(SQLAlchemyError)
def handle_database_error(e):
    logging.error(f"Database error: {str(e)}")
    return "Internal Server Error", 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Validate the user input to prevent IDOR attacks
    if not isinstance(username, str) or not isinstance(password, str):
        flash('Invalid user credentials', category='error')
        return redirect(url_for('index'))

    try:
        with Session() as session:
            user = session.query(User).filter_by(username=username).first()
            if user and ph.verify(password, user.password_hash):
                # Redirect the user to their account
                return redirect(url_for('account', username=username))
            else:
                flash('Invalid user credentials', category='error')
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")

    return redirect(url_for('index'))

@app.route('/view-profile/<username>')
def view_profile(username):
    try:
        with Session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                flash('User not found', category='error')
                return redirect(url_for('index'))

            # Access control: Only allow users to view their own profiles
            current_user = get_current_user()
            if username != current_user.username:
                flash('You do not have permission to view this profile', category='error')
                return redirect(url_for('index'))

            scores = {}
            for score in session.query(Score).filter_by(username=user.username):
                scores[score.id] = score.score
            return render_template('view-profile.html', username=username, scores=scores)
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")

    flash('Invalid user credentials', category='error')
    return redirect(url_for('index'))

@app.route('/account/<username>')
def account(username):
    try:
        with Session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                flash('User not found', category='error')
                return redirect(url_for('index'))

            scores = {}
            for score in session.query(Score).filter_by(username=user.username):
                scores[score.id] = score.score
            return render_template('account.html', username=username, scores=scores)
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")

    flash('Invalid user credentials', category='error')
    return redirect(url_for('index'))

@app.route('/view-profile/<username>/scores')
def view_scores(username):
    try:
        with Session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                flash('User not found', category='error')
                return redirect(url_for('index'))

            # Access control: Only allow users to view their own scores
            current_user = get_current_user()
            if username != current_user.username:
                flash('You do not have permission to view this profile', category='error')
                return redirect(url_for('index'))

            scores = {}
            for score in session.query(Score).filter_by(username=user.username):
                scores[score.id] = score.score
            return render_template('view-scores.html', username=username, scores=scores)
    except SQLAlchemyError as e:
        logging.error(f"Database error: {str(e)}")

    flash('Invalid user credentials', category='error')
    return redirect(url_for('index'))

def get_current_user():
    # Replace this with your own authentication logic
    return User.query.filter_by(username=current_app.config['CURRENT_USER']).first()

if __name__ == '__main__':
    app.run(debug=app.debug)

