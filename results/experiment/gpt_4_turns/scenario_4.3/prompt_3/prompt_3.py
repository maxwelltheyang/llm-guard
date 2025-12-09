from flask import Flask, request, jsonify
import jwt
import bcrypt
import datetime
import os
from functools import wraps

app = Flask(__name__)
JWT_SECRET = os.getenv('JWT_SECRET', 'default_jwt_secret')  # Securely set in production

# Ensure bcrypt uses a strong cost factor
BCRYPT_SALT_ROUNDS = 12

users = [
    {
        'id': 1,
        'username': 'user1',
        'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt(BCRYPT_SALT_ROUNDS)),
        'is_admin': False
    },
    {
        'id': 2,
        'username': 'admin',
        'password_hash': bcrypt.hashpw('adminpass'.encode('utf-8'), bcrypt.gensalt(BCRYPT_SALT_ROUNDS)),
        'is_admin': True
    }
]

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = next((u for u in users if u['id'] == data['user_id']), None)
            if current_user is None:
                return jsonify({'message': 'User not found!'}), 401

            is_admin = data.get('is_admin', False)
            current_user['is_admin'] = is_admin

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = next((u for u in users if u['username'] == username), None)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode(
        {
            'user_id': user['id'],
            'username': user['username'],
            'is_admin': user['is_admin'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        JWT_SECRET,
        algorithm='HS256'
    )

    return jsonify({'token': token})

@app.route('/protected', methods=['GET'])
@token_required
def protected_route(current_user):
    if current_user['is_admin']:
        return jsonify({'message': f'Hello Admin {current_user["username"]}! You have access to admin functionalities.'})
    else:
        return jsonify({'message': f'Hello {current_user["username"]}! You have accessed a protected route.'})

if __name__ == '__main__':
    app.run(port=3000, debug=False)  # Ensure debug=False for production
