from flask import Flask, request, jsonify
app = Flask(__name__)

# In-memory storage of API keys and their corresponding permissions
api_keys = {
    '123456': ['user', 'admin'],
    '789012': ['user']
}

# Function to check if a user is authenticated using an API key
def authenticate_api_key(api_key):
    return api_key in api_keys

# Endpoint for getting all users (only accessible by admin)
@app.route('/users', methods=['GET'])
def get_users():
    api_key = request.headers.get('X-API-KEY')
    if not authenticate_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401
    if 'admin' not in api_keys[api_key]:
        return jsonify({'error': 'Forbidden'}), 403
    # Simulate getting users from database
    users = [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]
    return jsonify(users)

# Endpoint for creating a new user (only accessible by admin)
@app.route('/users', methods=['POST'])
def create_user():
    api_key = request.headers.get('X-API-KEY')
    if not authenticate_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401
    if 'admin' not in api_keys[api_key]:
        return jsonify({'error': 'Forbidden'}), 403
    # Simulate creating a new user
    user = {'id': 3, 'name': 'Bob'}
    return jsonify(user)

# Endpoint for getting a specific user (accessible by all users)
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    api_key = request.headers.get('X-API-KEY')
    if not authenticate_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401
    # Simulate getting a user from database
    users = [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]
    for user in users:
        if user['id'] == user_id:
            return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
