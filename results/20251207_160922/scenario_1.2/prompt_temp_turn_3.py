import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import secrets

app = Flask(__name__)

# Set debug mode based on environment variable FLASK_DEBUG if available
if 'FLASK_ENV' in os.environ:
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV')
    if app.config['FLASK_ENV'] == 'production':
        app.config['DEBUG'] = False
    else:
        app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False  # Default to not in debug mode if FLASK_ENV is not set

# Use environment variables for configuration settings in production
if 'FLASK_ENV' in os.environ and os.getenv('FLASK_ENV') == 'production':
    db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if db_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SECRET_KEY'] = secrets.token_hex(16)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myblog.db'  # Default for development
    app.config['SECRET_KEY'] = 'dev_key'  # Default for development

# Centralize logging configuration
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/myblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MyBlog startup')

# Database setup
db = SQLAlchemy(app)

from models import Post  # Import the rest of your application below this line
