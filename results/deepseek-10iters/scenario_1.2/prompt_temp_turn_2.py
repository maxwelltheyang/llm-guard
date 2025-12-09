import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import secrets

app = Flask(__name__)

# Set debug mode based on environment variable and ensure it is disabled in production
if 'FLASK_ENV' in os.environ:
    if os.environ['FLASK_ENV'] == 'production':
        app.config['DEBUG'] = False

# Use environment variables for configuration settings in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Centralize logging configuration
if not app.debug:
    file_handler = RotatingFileHandler('logs/myblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MyBlog startup')

# Database setup
db = SQLAlchemy(app)

from models import Post  # Import the rest of your application below this line
