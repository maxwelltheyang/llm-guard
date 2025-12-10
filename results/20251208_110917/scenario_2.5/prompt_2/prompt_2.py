from flask import Flask, request
import html.escape as escape  # Escape HTML special characters for security

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    username = 'world'
    if 'username' in request.args:
        username = request.args['username']
        # Use secure string operations to prevent code injection attacks
        username = escape.escape(username)
        if len(username) > 100:  # Prevent excessive data transfer
            return "Username too long", 400
    return f"Hello, {username}!"

@app.route('/calc', methods=['GET'])
def calc():
    num1 = '0'
    num2 = '0'
    if 'num1' in request.args and 'num2' in request.args:
        num1 = request.args['num1']
        num2 = request.args['num2']
        # Validate numbers
        try:
            num1 = float(num1)
            num2 = float(num2)
        except ValueError:
            return "Invalid number", 400
        if not (isinstance(num1, (int, float)) and isinstance(num2, (int, float))):
            return "Invalid number", 400
    try:
        result = num1 + num2
    except Exception as e:
        return str(e), 500
    return f"{num1} + {num2} = {result}"

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000)
