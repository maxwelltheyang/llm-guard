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
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SecureLogger:
    def __init__(self, logger):
        self.logger = logger

    def error(self, message):
        self.logger.error(message)

secure_logger = SecureLogger(logger)

def get_secret_key():
    secret_key = os.environ.get('APP_SECRET_KEY')
    if not secret_key:
        raise Exception("SECRET_KEY is not set")
    return secret_key

secret_key = get_secret_key()

class URLSafeSerializerWithKey(URLSafeSerializer):
    def __init__(self, key):
        super().__init__(key)

serializer = URLSafeSerializerWithKey(secret_key)

# ...

if __name__ == '__main__':
    try:
        app.run(debug=False)
    except Exception as e:
        secure_logger.error(f"Failed to run application: {str(e)}")
        exit(1)
