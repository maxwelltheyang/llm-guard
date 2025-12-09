import os
from flask import Flask, session, redirect, url_for, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()  # Load environment variables from a .env file

# Secret Key Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Database URI Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy(app)

# Model Definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Add Content-Security-Policy, X-Frame-Options, and X-Content-Type-Options headers for enhanced security
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Debug Mode Configuration
app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development' if not app.config['DEBUG'] else False

from flask import Flask, request, render_template, redirect, url_for, session

# Routes and other configurations...

if __name__ == '__main__':
    db.create_all()
    app.run(debug=app.config['DEBUG'])
