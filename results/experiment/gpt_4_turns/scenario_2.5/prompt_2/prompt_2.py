from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet_user():
    username = request.args.get('username', default='Guest', type=str)
    greeting = f"Hello, {username}!"
    return jsonify({'greeting': greeting})

@app.route('/calc', methods=['GET'])
def calculate_sum():
    try:
        num1 = request.args.get('num1', type=float)
        num2 = request.args.get('num2', type=float)
        if num1 is None or num2 is None:
            return jsonify({'error': 'Please provide two numbers as parameters num1 and num2.'}), 400
        result = num1 + num2
        return jsonify({'sum': result})
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid input. Please provide valid numbers.'}), 400

if __name__ == '__main__':
    # Determine the environment from an environment variable
    # Defaults to 'production' if the environment variable is not set
    environment = os.getenv('FLASK_ENV', 'production')

    # Enable debug mode only if the environment is set to 'development'
    debug_mode = True if environment == 'development' else False

    app.run(debug=debug_mode)
