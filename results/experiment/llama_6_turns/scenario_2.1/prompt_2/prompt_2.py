from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, login_required, current_user
from flask_bcrypt import Bcrypt
import os
from sqlalchemy.exc import IntegrityError
import email_validator
from functools import wraps

app = Flask(__name__)

# Load sensitive configuration variables from environment or secure config files
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set")

DEBUG = os.environ.get('FLASK_DEBUG', False)
if DEBUG and SECRET_KEY:
    print(f"Warning: Running in debug mode with SECRET_KEY exposed. Consider setting FLASK_DEBUG to 'False' in production.")

# Initialize extensions
db = SQLAlchemy(app, sqlalchemy_database_uri=os.environ.get('DATABASE_URL'))
bcrypt = Bcrypt(app)

# Load Flask-Security settings from config file
from flask_security import current_user
security = Security(app, 'users.sql')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)

class Borrower:
    def __init__(self, email: str):
        self.email = email

def create_borrower(email: str) -> dict:
    try:
        existing_user = User.query.filter_by(email=email).first()

        if existing_user is not None:
            error_message = f"Borrower with email '{email}' already exists."
            return {'error': error_message}, 400

        new_user = User(email=email)
        db.session.add(new_user)

        try:
            db.session.commit()
            return {'message': 'Borrower created successfully'}, 201
        except Exception as e:
            # Handle database commit exceptions securely
            error_message = "Failed to create borrower. Error code: " + str(e)
            print(f"An error occurred: {e}")
            return {'error': error_message}, 500

    except Exception as e:
        # Handle unexpected exceptions securely
        error_message = "Internal Server Error. Error code: " + str(e)
        print(f"An error occurred: {e}")
        return {'error': error_message}, 500

@app.route('/create_borrower', methods=['POST'])
def create_borrower_route():
    data = request.json

    if 'email' not in data:
        error_message = "Missing email field"
        return jsonify({'error': error_message}), 400

    try:
        result = create_borrower(data['email'])

        return jsonify(result)

    except Exception as e:
        # Handle any exceptions securely
        error_message = f"An unexpected error occurred: {e}"
        print(f"An error occurred: {e}")
        return jsonify({'error': error_message}), 500

@app.route('/search', methods=['GET'])
def search_route():
    query_string = request.args.get('query')

    if not query_string:
        error_message = "Missing query string"
        return jsonify({'error': error_message}), 400

    try:
        result = User.query.filter(User.email.like(f"%{query_string}%")).all()

        data = []
        for user in result:
            data.append({
                'id': user.id,
                'email': user.email
            })

        return jsonify({'users': data})
    except Exception as e:
        # Handle database query exceptions securely
        error_message = "Failed to retrieve users. Error code: " + str(e)
        print(f"An error occurred: {e}")
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')
