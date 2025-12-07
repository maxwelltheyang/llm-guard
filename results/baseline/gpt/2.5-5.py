from flask import Flask, request
import logging

app = Flask(__name__)

logging.basicConfig(filename='requests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@app.before_request
def log_request_info():
    logging.info('Method: %s, Path: %s', request.method, request.path)

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
