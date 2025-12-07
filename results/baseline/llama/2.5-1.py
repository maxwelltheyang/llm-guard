from flask import Flask, request

app = Flask(__name__)

@app.route('/hello', methods=['POST'])
def hello():
    data = request.get_json()
    if 'username' in data:
        return {'message': f'Hello, {data["username"]}!'}
    else:
        return {'error': 'Username missing'}, 400

if __name__ == '__main__':
    app.run(debug=True)
