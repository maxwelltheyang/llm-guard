from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Set up logging to a file
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path}")

@app.route('/greet', methods=['GET'])
def greet_user():
    username = request.args.get('username', 'Guest')
    return jsonify({'message': f'Hello, {username}!'})

@app.route('/calc', methods=['GET'])
def calculate_sum():
    try:
        num1 = float(request.args.get('num1', 0))
        num2 = float(request.args.get('num2', 0))
    except ValueError:
        return jsonify({'error': 'Invalid input, please provide valid numbers.'}), 400

    result = num1 + num2
    return jsonify({'sum': result})

if __name__ == '__main__':
    # Determine the environment from an environment variable
    # Defaults to False for production
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']

    # Read host and port from environment variables with sensible defaults
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))

    # Ensure the application runs on the desired host and port
    app.run(debug=debug_mode, host=host, port=port)
