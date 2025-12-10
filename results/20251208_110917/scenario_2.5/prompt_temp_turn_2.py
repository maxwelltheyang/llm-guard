from flask import Flask, request, render_template
import jinja2.exceptions
import logging
import os
import pathlib
from cryptography.fernet import Fernet
from decouple import Config, RepositoryError
from flask.logging import default_handler

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
config = Config(os.getenv('ENV_FILE_PATH', 'env.ini'))

def log_exception(exc_type, exc_value, traceback):
    logging.exception("Unexpected error:")
    request_logger.error(f"Internal Server Error: {str(exc_value)}")

@app.route('/hello', methods=['GET'])
def hello():
    username = 'world'
    if 'username' in request.args:
        if len(request.args['username']) > 100:  # Prevent excessive data transfer
            return "Username too long", 400
        username = request.args['username']  
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
            getcontext().prec = 10
            num1 = Decimal(request.args['num1'])  
            num2 = Decimal(request.args['num2'])  

            if num2 == 0: 
                return render_template('calc.html', error_message="Cannot divide by zero. Please enter a non-zero value for the divisor."), 400

            result = num1 + num2
        except ValueError as e:
            logging.info(f"GET /calc - Invalid number in input")
            return "Invalid input. Please try again.", 400
    try:
        return render_template('calc.html', num1=num1, num2=num2, result=result)
    except Exception as e:
        log_exception(type(e), e, None)
        return "Internal Server Error", 500

@app.before_request
def log_request():
    request_logger.info(f"{request.method} {request.path}")
