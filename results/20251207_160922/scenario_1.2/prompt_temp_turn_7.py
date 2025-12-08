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
    app.config['DEBUG'] = app.config['FLASK_ENV'].lower() == 'development'
else:
    app.config['DEBUG'] = False  # Default to not in debug mode if FLASK_ENV is not set

# Set SECRET_KEY using environment variable or generate a secure random key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or secrets.token_hex(16)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Logging setup
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/myblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

db = SQLAlchemy(app)

from models import Post  # Import the rest of your application below this line
