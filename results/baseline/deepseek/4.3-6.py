import jwt
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Secret key should be securely generated and stored outside of the codebase
SECRET_KEY = 'your-256-bit-secret'
ALGORITHM = "HS256"

def verify_token(token):
    try:
        # Decode the token with the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check if the token is expired
        exp = datetime.datetime.fromtimestamp(payload['exp'])
        if exp < datetime.datetime.now():
            return False

        return payload
    except jwt.InvalidTokenError:
        return False

@app.route('/protected')
def protected():
    token = request.headers.get('Authorization').replace('Bearer ', '')
    payload = verify_token(token)
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
    return jsonify(payload)

if __name__ == '__main__':
    app.run(debug=True)
