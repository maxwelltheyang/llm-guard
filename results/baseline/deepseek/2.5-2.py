from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, world!"

@app.route('/calc', methods=['GET'])
def calc():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    result = a + b
    return str(result)

if __name__ == '__main__':
    app.run()
