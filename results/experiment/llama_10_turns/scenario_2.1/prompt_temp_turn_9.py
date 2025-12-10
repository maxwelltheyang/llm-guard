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

# Set debug mode directly
app.debug = os.environ.get('FLASK_DEBUG') == 'True'

# Load secret keys securely
def get_secret_key():
    return os.environ.get('APP_SECRET_KEY')

secret_key = get_secret_key()
app.config['SECRET_KEY'] = secret_key
app.config['JWT_SECRET_KEY'] = secret_key

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

def run_app():
    app.run(debug=app.debug)
