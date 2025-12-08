import ast
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Rate limiting configuration
RATE_LIMIT = 10
LAST_REQUEST_TIMES = {}

@app.route('/calc', methods=['GET'])
def calc():
    expr = request.args.get('expr', '0')
    try:
        # Validate the expression to ensure it's safe and expected format
        if not is_safe_expression(expr):
            raise ValueError("Invalid expression")

        # Safely evaluate the expression using ast.literal_eval
        result = safe_eval(expr)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def is_safe_expression(expression):
    try:
        # Parse the expression to check its syntax and structure
        ast.parse(expression, mode='eval')
        # Additional checks can be added here if necessary
        return True
    except SyntaxError:
        return False

def safe_eval(expression):
    try:
        # Safely evaluate the expression using ast.literal_eval
        node = ast.parse(expression, mode='eval')
        body = compile(node, '', 'eval')
        return ast.literal_eval(body)
    except (SyntaxError, NameError):
        raise ValueError("Invalid expression")

@app.route('/rate-limit', methods=['GET'])
def rate_limit():
    current_time = time.time()
    username = request.headers.get('X-Username')  # Assuming the user ID is provided in the header
    if not username or username not in LAST_REQUEST_TIMES:
        return jsonify({"error": "User not found"}), 404
    update_rate_limit_headers(response)
    return response

def update_rate_limit_headers(response):
    current_time = time.time()
    username = request.headers.get('X-Username')  # Assuming the user ID is provided in the header
    if not username:
        raise ValueError("User ID is required")
    response.headers['X-RateLimit-Remaining'] = str(max(0, RATE_LIMIT - len(LAST_REQUEST_TIMES[username])))
    response.headers['X-RateLimit-Reset'] = max(1, int(60 - (current_time - LAST_REQUEST_TIMES[username][-1])))

if __name__ == '__main__':
    app.run(debug=False)
