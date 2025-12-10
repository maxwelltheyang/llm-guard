from flask import Flask, request, render_template
import jinja2.exceptions
import logging
import os
import pathlib
from cryptography.fernet import Fernet
from decouple import Config, RepositoryError
from flask.logging import default_handler
import decimal
from packaging import version
import re

# Load configuration securely using `decouple`
config = Config(os.getenv('ENV_PATH', 'env'))

app = Flask(__name__)

# Set up logging configuration with a secure handler to prevent sensitive data exposure
log_format = '%(asctime)s - %(message)s'
handler = logging.FileHandler('request_log.log')
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
logging.getLogger().addHandler(default_handler)
logging.getLogger().removeHandler(handler)

def rotate_logs():
    max_bytes = 10 * 1024 * 1024
    backup_count = 5

    handler_maxBytes = handler.maxBytes
    handler_backupCount = handler.backupCount

    if isinstance(handler_maxBytes, int) and handler_maxBytes > 0:
        handler.maxBytes = max_bytes

    if isinstance(handler_backupCount, int) and handler_backupCount > 0:
        handler.backupCount = backup_count

# Set up a secure logging configuration
request_logger = logging.getLogger('requests')
rotator = logging.handlers.RotatingFileHandler(
    'request_log.log',
    encoding='utf-8',
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)
formatter = logging.Formatter(log_format)
rotator.setFormatter(formatter)
request_logger.addHandler(rotator)

# Set up cryptography key management
secret_key = config.get('SECRET_KEY')
if secret_key is None:
    secret_key = Fernet.generate_key()
    config['SECRET_KEY'] = secret_key

cryptography = Fernet(secret_key)

def log_exception(exc_type, exc_value, traceback):
    request_logger.error(f"Internal Server Error: {str(exc_value)}")
    logging.exception("Unexpected error:")

from decimal import Decimal as _Decimal
getcontext().prec = 999  # Set a higher precision for robustness

# Check and update dependencies
try:
    cryptography_version = version.parse(cryptography.__version__)
    if cryptography_version < version.parse('39.0'):
        raise ImportError("cryptography version is outdated")
except (ImportError, Exception):
    import pip
    try:
        pip.main(['install', 'cryptography>=39'])
    except Exception as e:
        request_logger.error(f"Failed to update cryptography: {str(e)}")

try:
    # Simulate dependency check and update process
    import requests

    # If the requests library is not installed, install it
    if 'requests' not in globals():
        import pip
        try:
            pip.main(['install', 'requests'])
        except Exception as e:
            request_logger.error(f"Failed to install requests: {str(e)}")
except ImportError:
    # If an exception occurs during the dependency check or update process,
    # log the error and continue running the application
    request_logger.error("An error occurred during dependency check or update")

# Set up a secure encryption key for cryptography
cryptography_key = secret_key

@app.before_request
def log_request():
    request_logger.warning(f"{request.method} {request.path}")

@app.route('/calc', methods=['GET'])
def calculate():
    try:
        num1 = float(request.args.get('num1'))
        num2 = float(request.args.get('num2'))

        if not (isinstance(num1, (int, float)) and isinstance(num2, (int, float))):
            return render_template('calc.html', error_message="Invalid input. Please enter a number.")

        try:
            result = num1 / num2
        except ZeroDivisionError:
            logging.info(f"GET /calc - Division by zero")
            return render_template('calc.html', error_message="Cannot divide by zero. Please enter a non-zero value for the divisor."), 400

        return render_template('calc.html', num1=num1, num2=num2, result=result)
    except Exception as e:
        request_logger.error(f"An error occurred: {str(e)}")
        return "Internal Server Error", 500
