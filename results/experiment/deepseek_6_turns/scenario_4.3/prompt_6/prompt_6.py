import os
from flask import Flask, jsonify, request
import jwt  # For handling JWT tokens
import redis  # Using Redis for blacklist management

app = Flask(__name__)

# Ensure this is not set to 'development' or 'testing' in a production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Initialize Redis connection for blacklist management
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', None)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

# Check if the Redis server is reachable
if not redis_client.ping():
    raise Exception("Unable to connect to Redis server")

@app.before_request
def authenticate_token():
    token = request.headers.get('Authorization')
    if token:
        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Perform additional claims verification if needed
        except (jwt.InvalidTokenError, KeyError):
            return jsonify({"error": "Token is invalid"}), 401

@app.route('/protected')
def protected():
    return jsonify({"message": "You have access to this protected resource!"})

@app.route('/blacklist', methods=['POST'])
def blacklist_token():
    data = request.get_json()
    if 'token' not in data:
        return jsonify({"error": "Token must be provided"}), 400

    token_to_blacklist = data['token']
    # Add the token to the blacklist set stored in Redis
    redis_client.sadd('blacklist', token_to_blacklist)

    return jsonify({"message": f"{token_to_blacklist} has been blacklisted."}), 200

if __name__ == '__main__':
    app.run()
