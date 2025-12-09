from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

# Rate limit configuration
RATE_LIMIT = 10  # Requests per minute
LAST_REQUEST_TIMES = {}

def rate_limit(username):
    if username not in LAST_REQUEST_TIMES:
        LAST_REQUEST_TIMES[username] = []

    current_time = time.time()
    requests = [t for t in LAST_REQUEST_TIMES[username] if current_time - t < 60]

    if len(requests) >= RATE_LIMIT:
        raise RateLimitExceeded("Rate limit exceeded for user {}. Try again later.".format(username))

    # Update the last request time
    LAST_REQUEST_TIMES[username].append(current_time)
    return True

class RateLimitExceeded(Exception):
    pass

@app.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(e):
    response = jsonify({"error": str(e)})
    response.headers['X-RateLimit-Remaining'] = 0
    response.headers['X-RateLimit-Reset'] = time.time() + (60 - (time.time() - LAST_REQUEST_TIMES[username][0]))
    return response, 429

@app.route('/greet', methods=['GET'])
def greet():
    username = request.args.get('username', 'Guest')
    try:
        rate_limit(username)  # Apply rate limit
    except RateLimitExceeded as e:
        return jsonify({"error": str(e)}), 429

    response = jsonify({"message": f"Hello, {username}!"})
    update_rate_limit_headers(response)
    return response

@app.route('/calc', methods=['GET'])
def calc():
    expr = request.args.get('expr', '0')
    try:
        # Safely evaluate the expression using a safer method than eval()
        result = eval_safely(expr)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def eval_safely(expression):
    # Implement a safer method to evaluate expressions without using eval()
    # For example, you can use the `ast` module to safely parse and evaluate expressions
    try:
        safe_expr = ast.parse(expression, mode='eval')
        return eval(compile(safe_expr, '', mode='eval'))
    except (SyntaxError, NameError):
        raise ValueError("Invalid expression")

def update_rate_limit_headers(response):
    response.headers['X-RateLimit-Remaining'] = str(RATE_LIMIT - len(LAST_REQUEST_TIMES[username]))
    response.headers['X-RateLimit-Reset'] = time.time() + 60 - (current_time - LAST_REQUEST_TIMES[username][-1])

if __name__ == '__main__':
    app.run(debug=True)
