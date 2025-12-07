from flask import Flask, request

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    username = request.args.get('username')
    if not username:
        return 'Please provide a username.', 400
    return f'Hello {username}!', 200

if __name__ == '__main__':
    app.run(debug=False)
