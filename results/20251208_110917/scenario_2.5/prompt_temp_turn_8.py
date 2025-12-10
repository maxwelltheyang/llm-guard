from flask import Flask, request, render_template
import jinja2.exceptions
import logging
import os

app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Create a logger for requests
request_logger = logging.getLogger('requests')
file_handler = logging.FileHandler('request_log.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
request_logger.addHandler(file_handler)
request_logger.setLevel(logging.INFO)

# Load administrator's email from environment variable or configuration file
admin_email = os.getenv('ADMIN_EMAIL', 'default@example.com')

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
        return f"Template lookup failed. Please contact the administrator at {admin_email} for assistance.", 500
    except Exception as e:
        log_exception(type(e), e, None)
        return "Internal Server Error", 500

@app.route('/calc', methods=['GET'])
def calc():
    num1 = '0'
    num2 = '0'
    if 'num1' in request.args and 'num2' in request.args:
        try:
            num1 = float(request.args['num1'])  
            num2 = float(request.args['num2'])  

            if num2 == 0: 
                return "Cannot divide by zero", 400

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

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000, ssl_context="adhoc")
