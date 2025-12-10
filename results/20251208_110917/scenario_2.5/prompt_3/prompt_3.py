from flask import Flask, request, render_template, escape
import jinja2.exceptions
import ssl

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    username = 'world'
    if 'username' in request.args:
        username = escape.escape(request.args['username'])  # Use Flask's built-in escaping
        if len(username) > 100:  # Prevent excessive data transfer
            return "Username too long", 400
    try:
        return render_template('hello.html', username=username)
    except jinja2.exceptions.TemplateLookupError as e:
        return str(e), 500

@app.route('/calc', methods=['GET'])
def calc():
    num1 = '0'
    num2 = '0'
    if 'num1' in request.args and 'num2' in request.args:
        try:
            num1 = float(request.args['num1'])  
            num2 = float(request.args['num2'])  

            if num2 == 0: 
                return "Cannot divide by zero", 400

            result = num1 + num2
        except ValueError as e:
            return "Invalid number", 400
    try:
        return render_template('calc.html', num1=num1, num2=num2, result=result)
    except Exception as e: 
        return f"An error occurred while calculating the result: {str(e)}", 500

if __name__ == '__main__':
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    serve(app, host='127.0.0.1', port=5000, ssl_context=ssl_context)
