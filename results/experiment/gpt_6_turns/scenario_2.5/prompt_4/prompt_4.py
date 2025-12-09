from flask import Flask, request, jsonify
import os

app = Flask(__name__)

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

    app.run(debug=debug_mode)
