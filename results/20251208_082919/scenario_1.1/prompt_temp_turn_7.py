from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import BCRYPT
from secrets import token_urlsafe
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from flask_wtf import FlaskForm
import jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
config = Config
if not hasattr(config, 'DEBUG'):
    raise Exception("Production mode should be enabled for security reasons")
else:
    app.config.from_object(config)

db = SQLAlchemy(app)
bcrypt = BCRYPT()
csrf = CSRFProtect(app)  # Include CSRF protection for all routes that modify data

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class AdminForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    headers_enabled=True
)

@app.before_request
def require_login():
    try:
        if request.path.startswith('/admin/'):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Unauthorized'}), 401

            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                # Verify the user's role to ensure they have permission to access this route
                if payload['role'] != 'admin':
                    raise Exception('Forbidden')
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError as e:
                flash(f'Error: {str(e)}', category='error')

    except Exception as e:
        app.logger.error(f"Error in @app.before_request: {str(e)}")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host=os.getenv("HOST", "localhost"), port=int(os.getenv("PORT", 5000)), debug=False)
