import ast
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Rate limiting configuration
RATE_LIMIT = 10
LAST_REQUEST_TIMES = {}

# Allowed operations and functions in the safe evaluation context
ALLOWED_OPERATIONS = {
    ast.Add(),
    ast.Sub(),
    ast.Mult(),
    ast.Div(),
    ast.Pow(),
    ast.BitOr(),
    ast.BitAnd(),
    ast.LShift(),
    ast.RShift(),
    ast.FloorDiv(),
}

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
    def _safe_eval(node):
        if isinstance(node, ast.Expression):
            return _safe_eval(node.body)
        elif isinstance(node, ast.BinOp):
            left = _safe_eval(node.left)
            right = _safe_eval(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                return eval(f"{left} {str(node.op)} {right}")
        elif isinstance(node, ast.UnaryOp):
            operand = _safe_eval(node.operand)
            if isinstance(node.op, ast.USub):
                return -operand
        elif isinstance(node, ast.Num):
            return node.n
        else:
            raise ValueError("Unsupported operation")

    try:
        tree = ast.parse(expression, mode='eval')
        return _safe_eval(tree.body)
    except (SyntaxError, NameError, TypeError) as e:
        raise ValueError(f"Invalid expression: {str(e)}")

@app.route('/rate-limit', methods=['GET'])
def rate_limit():
    current_time = time.time()
    username = request.headers.get('X-Username')  # Assuming the user ID is provided in the header
    if not username:
        return jsonify({"error": "User ID is required"}), 400

    while LAST_REQUEST_TIMES.get(username, []) and current_time - LAST_REQUEST_TIMES[username][-1] < 60:
        time.sleep(1)  # Wait until the next allowed request time

    if len(LAST_REQUEST_TIMES.setdefault(username, [])) >= RATE_LIMIT:
        reset_time = int(60 - (current_time - LAST_REQUEST_TIMES[username][-1]))
        return jsonify({"error": "Rate limit exceeded", "reset_in": reset_time}), 429

    LAST_REQUEST_TIMES[username].append(current_time)
    response = jsonify({"status": "OK"})
    update_rate_limit_headers(response)
    return response

def update_rate_limit_headers(response):
    username = request.headers.get('X-Username')
    if not username:
        raise ValueError("User ID is required")

    remaining = max(0, RATE_LIMIT - len(LAST_REQUEST_TIMES.get(username, [])))
    response.headers['X-RateLimit-Remaining'] = str(remaining)
    response.headers['X-RateLimit-Reset'] = str(int(60 - (time.time() - LAST_REQUEST_TIMES[username][-1] if LAST_REQUEST_TIMES.get(username) else 0)))

if __name__ == '__main__':
    app.run(debug=True)
