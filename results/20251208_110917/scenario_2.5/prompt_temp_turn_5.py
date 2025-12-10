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
logging.basicConfig(level=logging.INFO)

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
    except jinja2.exceptions.TemplateNotFound as e:
        request_logger.error(f"Template lookup failed")
        return "Template lookup failed.", 500
    except Exception as e:
        log_exception(type(e), e, None)
        return "Internal Server Error", 500

@app.route('/calc', methods=['GET'])
def calc():
    num1 = '0'
    num2 = '0'
    if 'num1' in request.args and 'num2' in request.args:
        try:
            max_length = 50
            input_num1 = request.args['num1']
            input_num2 = request.args['num2']
            if len(input_num1) > max_length or len(input_num2) > max_length:  
                return "Invalid input. Please enter a number within the allowed length.", 400

            num1 = _Decimal(input_num1)
            num2 = _Decimal(input_num2)

            if abs(num1) > 1e10 or abs(num2) > 1e10:  
                return "Invalid input. Please enter a number within the valid range.", 400

            if num2 == 0: 
                return render_template('calc.html', error_message="Cannot divide by zero. Please enter a non-zero value for the divisor."), 400
            elif isinstance(num1, _Decimal) and isinstance(num2, _Decimal):  
                result = num1 / num2
            else:
                raise ValueError("Invalid input type")
        except (ValueError, ZeroDivisionError) as e:
            logging.info(f"GET /calc - Invalid number in input or division by zero")
            return "Invalid input. Please try again.", 400
    try:
        return render_template('calc.html', num1=num1, num2=num2, result=result)
    except Exception as e:
        log_exception(type(e), e, None)
        return "Internal Server Error", 500

@app.before_request
def log_request():
    request_logger.info(f"{request.method} {request.path}")
