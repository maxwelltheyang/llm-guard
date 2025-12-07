import logging
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.before_request
def log_request():
    logging.debug(f'Request Method: {request.method}, Request Path: {request.path}')

# Example usage
if __name__ == '__main__':
    app.run()
