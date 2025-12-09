import os
from flask import Flask, request, redirect, url_for, render_template
from flask_debugtoolbar import DebugToolbarExtension

def create_app():
    app = Flask(__name__)

    # Configure the debug mode based on the environment
    def configure_app(app):
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'production':
            app.config['DEBUG'] = False
            # Generate a secret key securely and set it in the config
            app.config['SECRET_KEY'] = os.urandom(24)
            # Additional security configurations for production
        else:
            app.debug = True
            toolbar = DebugToolbarExtension()
            toolbar.init_app(app)

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

    return app

app = create_app()

if __name__ == '__main__':
    app.run()
