from flask import Flask, request
import logging

app = Flask(__name__)

logging.basicConfig(filename='flask_app.log', level=logging.ERROR)

@app.route('/hello', methods=['GET'])
def hello():
    try:
        username = request.args.get('username')
        if not (0 < len(username) <= 50):
            return 'Username must be between 1 and 50 characters.', 400
        if any(char in username for char in '<>:"/\\|?*'):
            return 'Invalid character in username.', 400
        return f'Hello {username}!', 200
    except ValueError as e:
        logging.error(f"Error in /hello route: Invalid input. {e}")
        return "Internal Server Error", 500

@app.route('/calc', methods=['GET'])
def calc():
    try:
        num1 = request.args.get('num1')
        num2 = request.args.get('num2')
        if not (num1 and num2):
            return 'Please provide two numbers.', 400
        try:
            sum_result = float(num1) + float(num2)
            return f'The sum is: {sum_result}', 200
        except ValueError as e:
            logging.error(f"Error in /calc route: Invalid number format. {e}")
            return 'Invalid number format. Please enter a valid number.', 400
    except TypeError as e:
        logging.error(f"Error in /calc route: Type mismatch for numbers. {e}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
