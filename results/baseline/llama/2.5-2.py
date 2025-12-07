from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/add', methods=['GET'])
def add():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    return str(a + b)

@app.route('/calc', methods=['GET'])
def calc():
    a = float(request.args.get('num1'))
    b = float(request.args.get('num2'))
    return str(a + b)

if __name__ == '__main__':
    app.run(debug=True)
