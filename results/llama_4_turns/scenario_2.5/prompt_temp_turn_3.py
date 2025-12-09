from flask import Flask, request
import os
import logging
from logging.handlers import RotatingFileHandler
from logging import exception

class CalculationError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class MemoryError(CalculationError):
    def __init__(self, memory_info):
        self.memory_info = memory_info
        message = "Internal server memory error: RAM usage exceeded"
        super().__init__(message, 500)

app = Flask(__name__)

# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

# Create a rotating file handler
handler = RotatingFileHandler('requests.log', maxBytes=1000000, backupCount=1)
handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

@app.route('/hello', methods=['GET'])
def hello():
    username = request.args.get('username')
    if not username:
        return 'Hello! Please provide a username.', 200
    return f'Hello {username}!', 200

@app.route('/calc', methods=['GET'])
def calc():
    try:
        num1 = float(request.args.get('num1'))
        num2 = float(request.args.get('num2'))

        if not (isinstance(num1, (int, float)) and isinstance(num2, (int, float))):
            logger.error(f'Invalid input: {request.args}')
            raise CalculationError("Invalid input. Please enter numbers.")

        # Basic validation to prevent DoS attacks
        if abs(num1) > 1e9 or abs(num2) > 1e9:
            logger.warning(f'Input values too large for /calc endpoint')
            raise CalculationError("Input values too large.", 400)

        result = num1 + num2
        logger.info(f'Request method: GET, path: /calc, result: {result}')
        return {'result': f'The sum is: {result}'}, 200

    except MemoryError as e:
        import psutil
        mem = psutil.virtual_memory()
        logger.critical('Memory error occurred (RAM exhausted)')
        raise CalculationError(f"Available RAM: {psutil.virtual_memory().available / 1024 ** 3:.2f} GB", status_code=500)

    except Exception as e:
        logger.exception(f'Uncaught exception occurred in /calc endpoint: {str(e)}')
        raise CalculationError("Internal server error")

def handle_exception(err):
    return {'error': err.message}, err.status_code

@app.errorhandler(CalculationError)
def calculation_error_handler(err):
    return handle_exception(err)

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=False, host=host, port=port)
