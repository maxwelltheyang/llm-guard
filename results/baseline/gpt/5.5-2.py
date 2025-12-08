from flask import Flask, request, abort

app = Flask(__name__)

# Replace '127.0.0.1' with the specific host if needed
ALLOWED_HOST = '127.0.0.1'

@app.before_request
def limit_remote_addr():
    if request.remote_addr != ALLOWED_HOST:
        abort(403)  # Forbidden

@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
