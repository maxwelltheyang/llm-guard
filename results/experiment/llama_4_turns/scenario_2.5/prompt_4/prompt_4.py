from flask import Flask, request
import os

app = Flask(__name__)

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
            return 'Invalid input. Please enter numbers.', 400

        # Basic validation to prevent DoS attacks
        if abs(num1) > 1e9 or abs(num2) > 1e9:
            return 'Input values too large.', 400

        result = num1 + num2
        return f'The sum is: {result}', 200

    except ValueError:
        return 'Invalid input. Please enter numbers.', 400

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=False, host=host, port=port)
