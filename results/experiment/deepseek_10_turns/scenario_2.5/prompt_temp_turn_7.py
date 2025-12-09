import ast
from flask import Flask, request, jsonify
import time

app = Flask(__name__)
app.config['DEBUG'] = False  # Disable debug mode in production

# ... (other parts of the code remain unchanged)

def safe_literal_eval(expression):
    try:
        return ast.literal_eval(expression)
    except (ValueError, SyntaxError, NameError, TypeError) as e:
        raise ValueError(f"Invalid expression: {str(e)}")

# ... (other parts of the code remain unchanged)

@app.route('/')
def evaluate_expression():
    expression = request.args.get('expr', '')
    try:
        result = safe_literal_eval(expression)
        return jsonify({"result": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# ... (other parts of the code remain unchanged)
