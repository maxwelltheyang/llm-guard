from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    username = request.args.get('username', type=str.strip)

    if not username:
        return 'Please provide a username.', 400

    if len(username) > 20:
        return 'Username too long.', 400

    return f'Hello {username}!', 200

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', 'localhost')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG') is not None

    print(f"Running on http://{host}:{port}")

    app.run(host=host, port=port, debug=debug)
