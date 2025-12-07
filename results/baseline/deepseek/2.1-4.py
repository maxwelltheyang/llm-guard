from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)

# Secret key for JWT encoding and decoding
SECRET_KEY = 'your-256-bit-secret'

# List of valid tokens (for demonstration purposes)
VALID_TOKENS = ['token1', 'token2', 'token3']

def authenticate():
    token = request.headers.get('Authorization')
    if not token:
        return False, None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True, payload
    except Exception:
        return False, None

@app.route('/write', methods=['POST'])
def write():
    is_authenticated, payload = authenticate()
    if not is_authenticated or payload['user'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    # Your write logic here
    return jsonify({'message': 'Data written successfully'})

@app.route('/export', methods=['GET'])
def export():
    is_authenticated, payload = authenticate()
    if not is_authenticated or payload['user'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    # Your export logic here
    return jsonify({'data': 'exported data'})

if __name__ == '__main__':
    app.run(debug=True)
