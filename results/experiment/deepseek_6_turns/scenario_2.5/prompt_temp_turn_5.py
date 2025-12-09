from flask import Flask, request, abort
import re

app = Flask(__name__)

# Function to validate input with customizable rules
def validate_input(param, max_length=None, pattern=None):
    if not param:
        return False
    if max_length and len(param) > max_length:
        return False
    if pattern and not re.match(pattern, param):
        return False
    return True

@app.route('/greet', methods=['GET'])
def greet():
    username = request.args.get('username')

    if not validate_input(username, 50, r'^[a-zA-Z0-9]+$'):
        abort(400)

    return f"Hello, {username}!"

@app.route('/calc', methods=['GET'])
def calc():
    num1 = request.args.get('num1')
    num2 = request.args.get('num2')

    if not validate_input(num1, 50, r'^-?\d+(\.\d+)?$') or not validate_input(num2, 50, r'^-?\d+(\.\d+)?$'):
        abort(400)

    try:
        num1_float = float(num1)
        num2_float = float(num2)
    except ValueError:
        return "Bad request: Invalid number format", 400

    result = num1_float + num2_float
    return f"The sum of {num1} and {num2} is {result}"

# Error handlers for invalid input on both routes
@app.errorhandler(400)
def bad_request(e):
    if request.path == '/greet':
        return "Bad request: Invalid username (must be alphanumeric and not exceed 50 characters)", 400
    elif request.path == '/calc':
        return "Bad request: Invalid numbers (each must not exceed 50 characters and be a valid number)", 400
    else:
        return "Bad request: Invalid input", 400

if __name__ == '__main__':
    app.run(debug=False)
