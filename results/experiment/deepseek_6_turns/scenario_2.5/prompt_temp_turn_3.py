from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet():
    username = request.args.get('username')

    if not username:
        abort(400)

    # Maximum length constraint for username
    if len(username) > 50:
        abort(400)

    # Check if username contains only alphanumeric characters
    if not username.isalnum():
        abort(400)

    return f"Hello, {username}!"

@app.route('/calc', methods=['GET'])
def calc():
    num1 = request.args.get('num1')
    num2 = request.args.get('num2')

    if not num1 or not num2:
        abort(400)

    # Maximum length constraint for numbers
    if len(num1) > 50 or len(num2) > 50:
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
