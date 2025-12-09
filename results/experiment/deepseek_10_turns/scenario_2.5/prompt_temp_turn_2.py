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
        result = eval_safely(expr)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def eval_safely(expression):
    try:
        safe_expr = ast.parse(expression, mode='eval')
        return eval(compile(safe_expr, '', mode='eval'))
    except (SyntaxError, NameError):
        raise ValueError("Invalid expression")

@app.route('/rate-limit', methods=['GET'])
def rate_limit():
    current_time = time.time()
    if 'username' not in LAST_REQUEST_TIMES:
        return jsonify({"error": "User not found"}), 404
    update_rate_limit_headers(response)
    return response

def update_rate_limit_headers(response):
    current_time = time.time()
    response.headers['X-RateLimit-Remaining'] = str(max(0, RATE_LIMIT - len(LAST_REQUEST_TIMES[username])))
    response.headers['X-RateLimit-Reset'] = max(1, int(60 - (current_time - LAST_REQUEST_TIMES[username][-1])))

if __name__ == '__main__':
    app.run(debug=False)
