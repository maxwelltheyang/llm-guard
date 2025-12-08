import jwt
from flask import request, jsonify, Flask

app = Flask(__name__)

# Secret key for decoding JWT
SECRET_KEY = 'your_secret_key'

def authenticate_jwt(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # You can add more checks here, e.g., check the user in your database
            return func(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    return wrapper

# Example protected route
@app.route('/protected')
@authenticate_jwt
def protected():
    return jsonify({'message': 'This is a protected endpoint'})

if __name__ == '__main__':
    app.run(debug=True)
