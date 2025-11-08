from flask import Flask, request, jsonify
app = Flask(__name__)

# Hard-coded secret for demonstration purposes only.
SECRET_KEY = "my_secret_key"

@app.route('/login', methods=['POST'])
def login():
    if 'username' in request.json and 'password' in request.json:
        username = request.json['username']
        password = request.json['password']

        # Check if the username is correct
        if username == "admin":
            # For demonstration purposes only, check if the password matches the SECRET_KEY.
            if password == SECRET_KEY:
                return jsonify({'status': 'success', 'message': 'Login successful!'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Invalid password'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Invalid username'}), 403

    # If the request is missing either the username or password, return an error.
    return jsonify({'status': 'error', 'message': 'Username and password required'}), 400

if __name__ == '__main__':
    app.run(debug=True)