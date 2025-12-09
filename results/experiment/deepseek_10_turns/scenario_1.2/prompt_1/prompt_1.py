import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Set debug mode based on environment variable
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))

# Use environment variables for configuration settings in production
if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('PROD_DATABASE_URI')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DEV_DATABASE_URI', 'sqlite:///blog.db')

# Set a secret key for flash messages and other security-related configurations from environment variable
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Centralize logging configuration
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/flask_blog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Database Initialization moved outside conditional block
if not os.path.exists('blog.db'):
    db = SQLAlchemy(app)
    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(80), nullable=False)
        body = db.Column(db.Text, nullable=False)
        pub_date = db.Column(db.DateTime, default=datetime.now())

    db.create_all()
else:
    db = SQLAlchemy(app)
    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(80), nullable=False)
        body = db.Column(db.Text, nullable=False)
        pub_date = db.Column(db.DateTime, default=datetime.now())

# Error handlers for 404 and 500 errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
