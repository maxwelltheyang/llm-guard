import os
from flask import Flask, request, redirect, url_for, render_template
from flask_debugtoolbar import DebugToolbarExtension
import logging

def create_app():
    app = Flask(__name__)

    # Configure the debug mode and secret key based on environment variables
    def configure_app(app):
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            app.config['DEBUG'] = False
            app.config['SECRET_KEY'] = get_secret_key()  # Use a function to securely generate the secret key
            configure_logging(app)
        else:
            app.debug = True

        # Set up logging here or in a separate function if needed
        configure_logging(app)

    configure_app(app)

    @app.route('/')
    def index():
        return "Hello, World!"

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            # Validate the user credentials securely (example placeholder)
            return redirect(url_for('index'))
        return render_template('login.html')

    @app.before_request
    def log_deletions():
        if request.method == 'DELETE':
            logger.info(f'User attempted to delete resource: {request.path}')  # Log detailed information

    return app

def get_secret_key():
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("No SECRET_KEY set for Flask application")
    return secret_key

def configure_logging(app):
    # Set up a basic logging configuration with appropriate levels
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

app = create_app()

if __name__ == '__main__':
    app.run()
