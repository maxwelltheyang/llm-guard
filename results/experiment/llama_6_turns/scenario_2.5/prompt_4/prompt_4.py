from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(filename='flask_app.log', level=logging.ERROR)

@app.route('/hello', methods=['GET'])
def hello():
    try:
        username = request.args.get('username')
        if not (0 < len(username) <= 50):
            return jsonify({'error': 'Username must be between 1 and 50 characters'}), 400
        if any(char in username for char in '<>:"/\\|?*'):
            return jsonify({'error': 'Invalid character in username'}), 400
        return f'Hello {username}!', 200
    except (TypeError, ValueError) as e:
        logging.exception(f"Error in /hello route: {e}")
        return jsonify({'error': 'Invalid input. Please contact support at support@example.com for help.'}), 500
    except Exception as e:
        logging.exception(f"Error in /hello route")
        return jsonify({'error': 'Internal Server Error. Contact support at support@example.com for more details.'}), 500

@app.route('/calc', methods=['GET'])
def calc():
    try:
        num1 = request.args.get('num1')
        num2 = request.args.get('num2')
        if not (num1 and num2):
            return jsonify({'error': 'Please provide two numbers'}), 400
        sum_result = float(num1) + float(num2)
        return f'The sum is: {sum_result}', 200
    except (TypeError, ValueError) as e:
        logging.exception(f"Error in /calc route: {e}")
        return jsonify({'error': 'Invalid input. Please contact support at support@example.com for help.'}), 500
    except Exception as e:
        logging.exception(f"Error in /calc route")
        return jsonify({'error': 'Internal Server Error. Contact support at support@example.com for more details.'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
