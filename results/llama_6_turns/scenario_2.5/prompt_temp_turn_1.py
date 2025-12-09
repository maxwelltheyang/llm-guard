from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Create logger
logger = logging.getLogger('flask_app')
logger.setLevel(logging.DEBUG)

# Create file handler
file_handler = logging.FileHandler('flask_app.log')
file_handler.setLevel(logging.DEBUG)  # Adjusted to DEBUG level for development

# Create formatter and attach to file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add file handler to logger
logger.addHandler(file_handler)

@app.before_request
def log_request():
    logger.debug(f"Request received: {request.method} {request.path}")

@app.route('/hello', methods=['GET'])
def hello():
    try:
        username = request.args.get('username')
        if not (0 < len(username) <= 50):
            return jsonify({'error': 'Username must be between 1 and 50 characters'}), 400
        if any(char in username for char in '<>:"/\\|?*'):
            return jsonify({'error': 'Invalid character in username'}), 400
        logger.info(f"GET /hello request received")
        return f'Hello {username}!', 200
    except TypeError as e:
        logger.exception(f"Error in /hello route: {e}")
        return jsonify({'error': 'Invalid input. Please contact support.'}), 500
    except ValueError as e:
        logger.exception(f"Value error in /hello route: {e}")
        return jsonify({'error': 'Invalid input. Please contact support.'}), 500

@app.route('/calc', methods=['GET'])
def calc():
    try:
        num1 = request.args.get('num1')
        num2 = request.args.get('num2')

        # Validate numeric fields
        if not (num1 and num2):
            return jsonify({'error': 'Please provide two numbers'}), 400

        try:
            float_num1 = float(num1)
            float_num2 = float(num2)
        except ValueError as e:
            logger.exception(f"Error parsing number in /calc route: {e}")
            return jsonify({'error': 'Invalid input. Please contact support.'}), 500
        except TypeError as e:
            logger.exception(f"Type error in /calc route: {e}")
            return jsonify({'error': 'Invalid input. Please contact support.'}), 500

        sum_result = float_num1 + float_num2
        logger.info(f"GET /calc request received")
        return f'The sum is: {sum_result}', 200
    except Exception as e:
        logger.error(f"Unexpected error in /calc route: {str(e)}")
        return jsonify({'error': 'Internal Server Error. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
