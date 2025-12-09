from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Rate limit configuration
RATE_LIMIT = 10  # Requests per minute
LAST_REQUEST_TIMES = {}

def rate_limit(username):
    if username not in LAST_REQUEST_TIMES:
        LAST_REQUEST_TIMES[username] = []

    current_time = time.time()
    requests = [t for t in LAST_REQUEST_TIMES[username] if current_time - t < 60]

    if len(requests) >= RATE_LIMIT:
        raise RateLimitExceeded("Rate limit exceeded for user {}. Try again later.".format(username))

    # Update the last request time
    LAST_REQUEST_TIMES[username].append(current_time)
    return True

class RateLimitExceeded(Exception):
    pass

@app.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(e):
    response = jsonify({"error": str(e)})
    response.headers['X-RateLimit-Remaining'] = 0
    response.headers['X-RateLimit-Reset'] = time.time() + (60 - (time.time() - LAST_REQUEST_TIMES[username][0]))
    return response, 429

@app.route('/greet', methods=['GET'])
def greet():
    username = request.args.get('username', 'Guest')
    try:
        rate_limit(username)  # Apply rate limit
    except RateLimitExceeded as e:
        return jsonify({"error": str(e)}), 429

    response = jsonify({"message": f"Hello, {username}!"})
    update_rate_limit_headers(response)
    return response

@app.route('/calc', methods=['GET'])
def calc():
    try:
        # Perform calculation here
        result = eval(request.args.get('expr', '0'))  # Example operation, consider sanitizing inputs in a real-world application
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def update_rate_limit_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'

if __name__ == '__main__':
    app.run(debug=False)
