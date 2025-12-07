import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

def authenticate(username, password):
    # hardcoded users and passwords
    users = {
        "admin": hashlib.sha256("password").hexdigest(),
        "user": hashlib.sha256("password123").hexdigest()
    }

    return users.get(username) == hashlib.sha256(password).hexdigest()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if authenticate(data['username'], data['password']):
        return jsonify({'token': 'secret-token'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
