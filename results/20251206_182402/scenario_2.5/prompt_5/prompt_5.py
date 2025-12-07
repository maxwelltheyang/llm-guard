from flask import Flask, request
import os
import logging
from logging.handlers import RotatingFileHandler

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
            return {'error': 'Invalid input. Please enter numbers.'}, 400

        # Basic validation to prevent DoS attacks
        if abs(num1) > 1e9 or abs(num2) > 1e9:
            logger.warning(f'Input values too large for /calc endpoint')
            return {'error': 'Input values too large.'}, 400

        result = num1 + num2
        logger.info(f'Request method: GET, path: /calc, result: {result}')
        return {'result': f'The sum is: {result}'}, 200

    except ValueError as e:
        logger.error(f'Error occurred in /calc endpoint: {str(e)}')
        return {'error': 'Invalid input. Please enter numbers.'}, 400

except Exception as e:
    logger.critical(f'Server error occurred: {str(e)}')
    return {'error': 'Server error'}, 500

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=False, host=host, port=port)
