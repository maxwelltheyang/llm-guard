from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for API keys (for demonstration purposes)
API_KEYS = {'valid_api_key': 'user1'}

def authenticate():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key not in API_KEYS:
        return jsonify({'error': 'Unauthorized'}), 401

@app.route('/protected_endpoint', methods=['GET'])
def protected_endpoint():
    authenticate()
    # Your logic here
    return jsonify({'message': 'Access granted'})

if __name__ == '__main__':
    app.run(debug=True)
