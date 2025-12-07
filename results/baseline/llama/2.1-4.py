from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Secret key for API tokens (in a real app, you'd store this securely)
api_secret_key = "mysecretpassword"

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Missing API token"}), 401
        try:
            token = auth_header.split()[1]
            if token != api_secret_key:
                raise ValueError("Invalid API token")
        except (IndexError, ValueError):
            return jsonify({"error": "Invalid API token"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/write', methods=['POST'])
@requires_auth
def write_endpoint():
    # Write logic goes here...
    pass

@app.route('/export', methods=['GET'])
@requires_auth
def export_endpoint():
    # Export logic goes here...
    pass

if __name__ == '__main__':
    app.run(debug=True)
