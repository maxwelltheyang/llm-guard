from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet_user():
    username = request.args.get('username', 'Guest')
    greeting = f"Hello, {username}!"
    return jsonify({"greeting": greeting})

@app.route('/calc', methods=['GET'])
def calculate_sum():
    try:
        num1 = float(request.args.get('num1', 0))
        num2 = float(request.args.get('num2', 0))
        total = num1 + num2
        return jsonify({"sum": total})
    except ValueError:
        return jsonify({"error": "Invalid input. Please provide valid numbers."}), 400

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
