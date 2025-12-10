from flask import Flask, request
import html.escape as escape  # Escape HTML special characters for security

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    username = 'world'
    if 'username' in request.args:
        username = request.args['username']
        # Use secure string operations to prevent code injection attacks
        username = escape.escape(username)
        if len(username) > 100:  # Prevent excessive data transfer
            return "Username too long", 400
    return f"Hello, {username}!"

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000)
