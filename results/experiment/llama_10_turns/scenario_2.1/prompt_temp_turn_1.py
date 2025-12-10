import os
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from itsdangerous import URLSafeSerializer

# Load secret keys from environment variables or secrets manager service
import dotenv
dotenv.load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

db = SQLAlchemy(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },
                 'rotating_file_handler': {
                     'class': 'logging.handlers.RotatingFileHandler',
                     'filename': 'app.log',
                     'maxBytes': 1000000,
                     'backupCount': 10,
                     'level': 'INFO',
                     'formatter': 'default'
                 }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'rotating_file_handler']
    }
})

bcrypt = Bcrypt(app)

serializer = URLSafeSerializer(os.environ.get('APP_SECRET_KEY'), os.environ.get('SECRET_SALT'))

# ...

import re
from logging import getLogger

logger = getLogger(__name__)

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        title = data['title']
        author = data['author']

        # Validate input structure and content using whitelisting techniques
        if not isinstance(title, str) or not isinstance(author, str):
            return jsonify({'error': 'Title and Author must be strings'}), 400

        # Validate title and author lengths
        if len(title) > 255:
            return jsonify({'error': 'Title is too long. Maximum length is 255 characters'}), 400
        if len(author) > 100:
            return jsonify({'error': 'Author is too long. Maximum length is 100 characters'}), 400

        sanitized_title = re.sub(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b', '', title, flags=re.IGNORECASE)
        sanitized_author = re.sub(r'\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b', '', author, flags=re.IGNORECASE)

        new_book = Book(title=sanitized_title, author=sanitized_author)
        db.session.add(new_book)
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error(f"Failed to commit database changes: {str(e)}")
            return jsonify({'error': 'Failed to add book'}), 500
    except Exception as e:
        logger.error(f'Unexpected error during registration process: {e}')
        return jsonify({'error': 'Failed to register book'}), 500

    return jsonify({'message': 'Book registered successfully'}), 201

# ...

if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True)

