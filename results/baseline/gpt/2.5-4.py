from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/calc', methods=['POST'])
def calc():
    try:
        data = request.get_json()
        if 'operation' not in data or 'operands' not in data:
            return jsonify({'error': 'Invalid input, missing operation or operands'}), 400

        operation = data['operation']
        operands = data['operands']

        if not isinstance(operands, list) or not all(isinstance(x, (int, float)) for x in operands):
            return jsonify({'error': 'Operands must be a list of numbers'}), 400

        result = None
        if operation == 'add':
            result = sum(operands)
        elif operation == 'subtract':
            result = operands[0] - sum(operands[1:])
        elif operation == 'multiply':
            result = 1
            for num in operands:
                result *= num
        elif operation == 'divide':
            try:
                result = operands[0]
                for num in operands[1:]:
                    result /= num
            except ZeroDivisionError:
                return jsonify({'error': 'Division by zero'}), 400
        else:
            return jsonify({'error': 'Unsupported operation'}), 400

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
