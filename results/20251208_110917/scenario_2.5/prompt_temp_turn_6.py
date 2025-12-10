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

app = Flask(__name__)

# Set up logging configuration with a secure handler to prevent sensitive data exposure
log_format = '%(asctime)s - %(message)s'
handler = logging.FileHandler('request_log.log')
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
logging.getLogger().addHandler(default_handler)
logging.getLogger().removeHandler(handler)
logging.basicConfig(level=logging.WARNING)

# Load configuration securely using `decouple`
config = Config(os.getenv('ENV_PATH', 'env'))

def log_exception(exc_type, exc_value, traceback):
    logging.exception("Unexpected error:")
    request_logger.error(f"Internal Server Error: {str(exc_value)}")

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
        logging.error(f"Failed to update cryptography: {str(e)}")

try:
    decouple_version = version.parse(decouple.__version__)
    if decouple_version < version.parse('4.0'):
        raise ImportError("decouple version is outdated")
except (ImportError, Exception):
    import pip
    try:
        pip.main(['install', 'python-dotenv>=4'])
    except Exception as e:
        logging.error(f"Failed to update decouple: {str(e)}")

@app.route('/hello', methods=['GET'])
def hello():
    username = 'world'
    if 'username' in request.args:
        max_length = 100
        input_username = request.args['username']
        if len(input_username) > max_length or not re.match('^[a-zA-Z0-9_]+$', input_username):  
            return "Invalid username. Please enter a string within the allowed length and format.", 400
        username = input_username  
    try:
        return render_template('hello.html', username=username)
    except jinja2.exceptions.TemplateLookupError as e:
        logging.error(f"Template lookup error: {str(e)}")
        return "Internal Server Error", 500

@app.route('/calc', methods=['GET'])
def calc():
    num1 = None
    num2 = None
    result = None
    try:
        if 'num1' in request.args and 'num2' in request.args:
            num1 = _Decimal(request.args.get('num1'))
            num2 = _Decimal(request.args.get('num2'))

            if abs(num1) > 1e10 or abs(num2) > 1e10:  
                return "Invalid input. Please enter a number within the valid range.", 400

            try:
                result = num1 / num2
            except ZeroDivisionError:
                logging.info(f"GET /calc - Division by zero")
                return render_template('calc.html', error_message="Cannot divide by zero. Please enter a non-zero value for the divisor."), 400
        else:
            return "Invalid input. Missing required parameters.", 400

        return render_template('calc.html', num1=num1, num2=num2, result=result)
    except (TypeError, ValueError) as e:
        logging.error(f"Invalid number in input: {str(e)}")
        return "Internal Server Error", 500

@app.before_request
def log_request():
    request_logger.warning(f"{request.method} {request.path}")
