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
        num1 = request.args.get('num1')
        num2 = request.args.get('num2')

        if num1 is None or num2 is None:
            raise ValueError("Missing input")

        num1 = float(num1)
        num2 = float(num2)

        total = num1 + num2
        return jsonify({"sum": total})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
