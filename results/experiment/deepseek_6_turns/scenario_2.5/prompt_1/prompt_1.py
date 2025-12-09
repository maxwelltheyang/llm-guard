from flask import Flask, request, abort
from validates import validate_alphanum

app = Flask(__name__)

@app.route('/greet', methods=['GET'])
def greet():
    username = request.args.get('username')

    if not username:
        return "Please provide a valid username", 400

    # Validate the username using validates library to ensure only alphanumeric characters are present
    if not validate_alphanum(username):
        abort(400)

    return f"Hello, {username}!"

# Error handler for invalid input
@app.errorhandler(400)
def bad_request(e):
    return "Bad request: Invalid username", 400

if __name__ == '__main__':
    app.run(debug=False)
