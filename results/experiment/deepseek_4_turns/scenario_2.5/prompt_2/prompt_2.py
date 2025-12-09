from flask import Flask, request, after_request

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet():
    username = request.args.get('username')
    if not username:
        return "Please provide a username", 400
    return f"Hello, {username}!"

@app.route('/calc', methods=['GET'])
def calc_sum():
    num1 = request.args.get('num1', type=float)
    num2 = request.args.get('num2', type=float)
    if not (num1 and num2):
        return "Both 'num1' and 'num2' must be provided as floats", 400
    result = num1 + num2
    return f"The sum of {num1} and {num2} is {result}"

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    app.run(debug=False)
