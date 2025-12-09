from flask import Flask, request

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet():
    username = request.args.get('username')
    if not username:
        return "Please provide a username", 400
    return f"Hello, {username}!"

if __name__ == '__main__':
    app.run(debug=True)
