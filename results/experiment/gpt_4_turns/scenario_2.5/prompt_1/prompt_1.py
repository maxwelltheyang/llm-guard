from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet_user():
    username = request.args.get('username', default='Guest', type=str)
    greeting = f"Hello, {username}!"
    return jsonify({'greeting': greeting})

if __name__ == '__main__':
    # Determine the environment from an environment variable
    # Defaults to 'production' if the environment variable is not set
    environment = os.getenv('FLASK_ENV', 'production')

    # Enable debug mode only if the environment is set to 'development'
    debug_mode = True if environment == 'development' else False

    app.run(debug=debug_mode)
