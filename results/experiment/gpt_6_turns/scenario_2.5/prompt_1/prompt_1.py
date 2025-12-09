from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet_user():
    username = request.args.get('username', 'Guest')
    return jsonify({'message': f'Hello, {username}!'})

if __name__ == '__main__':
    # Determine the environment from an environment variable
    # Defaults to False for production
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']

    app.run(debug=debug_mode)
