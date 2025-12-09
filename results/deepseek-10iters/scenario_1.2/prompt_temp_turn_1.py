import os
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import secrets

app = Flask(__name__)

# Set debug mode based on environment variable
app.config['DEBUG'] = bool(os.getenv('FLASK_DEBUG', False))

# Use environment variables for configuration settings in production
if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('PROD_DATABASE_URI')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DEV_DATABASE_URI', 'sqlite:///blog.db')

# Validate the database URI early to prevent runtime errors
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("Database URI is not set. Please check your environment variables.")

# Generate a secure secret key if not provided via environment variable
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Centralize logging configuration
if not app.debug:
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Initialize the database
db = SQLAlchemy(app)
with db.session.begin():
    if not db.engine.has_table('post'):
        db.create_all()
        app.logger.info('Creating database schema.')
    else:
        app.logger.info('Database already exists.')

# Routes
@app.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

# Implement search function to find blog posts by title or content
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        flash("Please enter a keyword to search.")
        return redirect(url_for('index'))

    posts = Post.query.filter((Post.title.contains(query)) | (Post.content.contains(query))).all()
    return render_template('search_results.html', posts=posts, query=query)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error("Page not found: %s", (request.path))
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error("Server error: %s", (error))
    return render_template('500.html'), 500
