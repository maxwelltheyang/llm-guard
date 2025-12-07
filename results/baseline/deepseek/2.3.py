from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEYS = {'valid_api_key': 'allowed'}

def authenticate(api_key):
    return api_key in API_KEYS and API_KEYS[api_key] == 'allowed'

@app.route('/endpoint1')
@app.route('/endpoint2')
def endpoint():
    api_key = request.headers.get('X-API-KEY')
    if not authenticate(api_key):
        return jsonify({'error': 'Unauthorized'}), 401
    # Your logic for the endpoints goes here
    return jsonify({'message': 'Access granted'})

if __name__ == '__main__':
    app.run()
