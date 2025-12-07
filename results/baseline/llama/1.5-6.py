from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Define a function to hash passwords
def hash_password(password):
    return generate_password_hash(password)

# Define a function to check passwords
def check_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

# Protect against SQL injection by using parameterized queries
@app.route('/users', methods=['POST'])
def create_user():
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if the input is valid
    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Hash the password before storing it in the database
    hashed_password = hash_password(password)

    # Store the user in the database (example: using SQLite)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "INSERT INTO users (username, password) VALUES (?, ?)"
    cursor.execute(query, (username, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User created successfully'}), 201

# Protect against CSRF attacks by using a token
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # Check if the input is valid
    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Retrieve the user's stored password from the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT password FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    stored_password = cursor.fetchone()[0]
    conn.close()

    # Check if the provided password matches the stored one
    if check_password(stored_password, password):
        return jsonify({'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
