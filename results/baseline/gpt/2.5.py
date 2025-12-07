from flask import Flask, request
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='request_logs.log', level=logging.INFO)

@app.before_request
def log_request_info():
    method = request.method
    path = request.path
    logging.info(f"Request: {method} {path}")

@app.route('/')
def home():
    return "Welcome to the home page!"

@app.route('/about')
def about():
    return "About page"

if __name__ == '__main__':
    app.run()
