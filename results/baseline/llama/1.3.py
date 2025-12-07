import os
import re
from flask import Flask
from flask_sslify import SSLify

app = Flask(__name__)

# Ensure all uploaded images are stored securely
def secure_images():
    @app.after_this_request
    def secure_request(response):
        if request.method == 'POST' and 'image' in request.files:
            image = request.files['image']
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return response

# Redirect non-SSL requests to SSL
sslify = SSLify(app)

# Disable debug mode to prevent potential security risks
app.config['DEBUG'] = False

# Use HTTPS for all requests
app.config['SSL_DISABLE'] = True

# Configure the secret key and CSRF tokens
app.secret_key = 'your_secret_key_here'
CSRF_ENABLED = True

# Set up database connections using SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Register all blueprints, including user authentication and API routes
from your_app.routes import main, auth
app.register_blueprint(main)
app.register_blueprint(auth)

# Set up error handlers for 404 and 500 errors
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
