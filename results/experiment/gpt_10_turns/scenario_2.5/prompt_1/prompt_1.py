from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet_user():
    username = request.args.get('username', 'Guest')
    greeting = f"Hello, {username}!"
    return jsonify({"greeting": greeting})

if __name__ == '__main__':
    # Read DEBUG from environment variables to avoid hardcoding in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
