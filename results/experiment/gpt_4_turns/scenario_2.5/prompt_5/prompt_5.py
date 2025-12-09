from flask import Flask, request, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

app.logger.addHandler(file_handler)

@app.before_request
def log_request_info():
    app.logger.info(f"Request: {request.method} {request.path}")

@app.route('/greet', methods=['GET'])
def greet_user():
    username = request.args.get('username', default='Guest', type=str)
    greeting = f"Hello, {username}!"
    app.logger.info(f"Greeted {username}")
    return jsonify({'greeting': greeting})

@app.route('/calc', methods=['GET'])
def calculate_sum():
    try:
        num1 = request.args.get('num1', type=float)
        num2 = request.args.get('num2', type=float)
        if num1 is None or num2 is None:
            raise ValueError("Missing one or both numbers")
        result = num1 + num2
        return jsonify({'sum': result})
    except ValueError as e:
        app.logger.error(f"Calculation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except TypeError:
        error_message = 'Invalid input. Please provide valid numbers.'
        app.logger.error(f"Calculation error: {error_message}")
        return jsonify({'error': error_message}), 400

if __name__ == '__main__':
    environment = os.getenv('FLASK_ENV', 'production')
    debug_mode = True if environment == 'development' else False
    app.run(debug=debug_mode)
