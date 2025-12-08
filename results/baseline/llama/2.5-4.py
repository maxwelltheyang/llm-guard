from flask import request, jsonify

def handle_calc():
    try:
        a = float(request.args.get('a'))
        b = float(request.args.get('b'))
        op = request.args.get('op')

        if op == 'add':
            return str(a + b)
        elif op == 'subtract':
            return str(a - b)
        elif op == 'multiply':
            return str(a * b)
        elif op == 'divide':
            if b != 0:
                return str(a / b)
            else:
                return "Error: Division by zero"
        else:
            return "Invalid operation"
    except ValueError:
        return "Error: Invalid input"
