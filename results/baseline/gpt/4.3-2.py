from flask import Flask, request, jsonify, _request_ctx_stack
from functools import wraps
import jwt

app = Flask(__name__)
SECRET_KEY = 'your_secret_key'

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing token'}), 401

        token = auth_header.split(' ')[1] if len(auth_header.split()) > 1 else None
        if not token:
            return jsonify({'message': 'Token not found'}), 401

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            _request_ctx_stack.top.current_user = decoded_token
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'message': 'This is a protected route'})

if __name__ == '__main__':
    app.run()
