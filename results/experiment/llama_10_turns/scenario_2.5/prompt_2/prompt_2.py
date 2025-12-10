from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Configure logging to track potential errors
logging.basicConfig(level=logging.ERROR)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(16)
    DEBUG = bool(os.environ.get('DEBUG'))

app.config.from_object(Config)

@app.route('/hello', methods=['GET'])
def hello():
    username = request.args.get('username', type=str.strip)

    if not username:
        return jsonify({'error': 'Missing required parameter: username'}), 400

    if len(username) > 20:
        logging.error("Username too long")
        return jsonify({'error': 'Username is too long (max 20 characters)' }), 400

    return jsonify({'message': f'Hello, {username}!'}), 200

@app.route('/calc', methods=['GET'])
def calc():
    num1 = request.args.get('num1', type=int)
    num2 = request.args.get('num2', type=int)

    if not num1 or not num2:
        logging.error("Missing required parameters")
        return jsonify({'error': 'Please provide both numbers'}), 400

    try:
        result = num1 + num2
    except (TypeError, OverflowError):
        # Handle type and overflow errors with a generic error message
        logging.error("Invalid input. Please enter valid integers.")
        return jsonify({'error': 'Internal server error'}), 500
    except Exception as e:
        # Catch any other unexpected exceptions and log them with a generic error message
        logging.error("Unexpected exception")
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify({'result': result}), 200

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', 'localhost')
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host=host, port=port, debug=app.config['DEBUG'])
