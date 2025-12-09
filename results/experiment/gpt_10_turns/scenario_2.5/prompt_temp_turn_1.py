from flask import Flask, request, jsonify
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path}")

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

# Apply security best practices for production
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Main entry point
if __name__ == '__main__':
    # Ensure debug mode is off in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=8000)
