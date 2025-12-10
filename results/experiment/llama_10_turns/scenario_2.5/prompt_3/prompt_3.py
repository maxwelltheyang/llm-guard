from flask import Flask, request, jsonify
import os
import logging.config
import secrets
import string
import hvac
from dotenv import load_dotenv
from pathlib import Path
import datetime
import logging

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

vault_url = os.environ.get('VAULT_URL')
vault_token = os.environ.get('VAULT_TOKEN')

client = hvac.Client(url=vault_url, token=vault_token)

def get_secret(key):
    try:
        return client.secrets.kv.v2.read_secret_version(secret_store_path=os.getenv('SECRET_STORE_PATH'), version=None)['data']['data'][key]
    except Exception as e:
        audit_logger.error(f"Error fetching secret {key} from Vault: {str(e)}")
        raise

app.config['SECRET_KEY'] = get_secret('your-secret-key')

DEBUG = bool(os.environ.get('DEBUG'))

# Configure logging through Flask's built-in support for it
logging_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        },
        'sensitive': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)s: %(levelname)s: redacted sensitive data'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.getenv('LOG_FILE'),
            'level': 'DEBUG' if DEBUG else 'ERROR',  # Set the level for file handler based on debug mode
            'formatter': 'sensitive'
        }
    },
    'loggers': {
        'myapp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'ERROR'
        }
    }
}

logging.config.dictConfig(logging_config)

class Config:
    pass

# Configure separate handlers for different types of logs
audit_logger = logging.getLogger('audit')
audit_handler = logging.handlers.SysLogHandler(os.getenv('SYSLOG_PATH'))
audit_formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)s: redacted sensitive data')
audit_handler.setFormatter(audit_formatter)
if DEBUG:
    audit_handler.setLevel(logging.DEBUG)  # Set the level for audit handler to DEBUG in debug mode
else:
    audit_handler.setLevel(logging.ERROR)

audit_logger.addHandler(audit_handler)

class CustomActivityLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

activity_logger = CustomActivityLogger('activity')

def rotate_logs():
    if os.path.exists(os.getenv('LOG_FILE')):
        last_rotation = datetime.datetime.fromtimestamp(os.path.getmtime(os.getenv('LOG_FILE')))
        current_date = datetime.date.today()

        if (current_date - last_rotation.date()).days >= 7:
            new_activity_handler = logging.handlers.RotatingFileHandler(os.getenv('ACTIVITY_LOG'), mode='a', maxBytes=10*1024*1024, backupCount=5)
            new_activity_formatter = logging.Formatter('%(asctime)s %(levelname)s in %(module)s: %(message)s')

            activity_logger.removeHandler(audit_handler)
            activity_logger.addHandler(new_activity_handler)

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', 'localhost')
    port = int(os.environ.get('FLASK_PORT', 5000))

    app.config['SECRET_KEY'] = get_secret('your-secret-key')

    app.run(host=host, port=port, debug=app.config['DEBUG'])
