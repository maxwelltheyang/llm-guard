from flask import Flask, request

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    username = request.args.get('username')
    if not username:
        return 'Hello! Please provide a username.', 200
    return f'Hello {username}!', 200

@app.route('/calc', methods=['GET'])
def calc():
    num1 = request.args.get('num1')
    num2 = request.args.get('num2')

    if not num1 or not num2:
        return 'Please provide two numbers.', 400

    try:
        result1 = float(num1)
        result2 = float(num2)
        return f'The sum is: {result1 + result2}', 200
    except ValueError:
        return 'Invalid input. Please enter a number.', 400

if __name__ == '__main__':
    app.run(debug=False)
