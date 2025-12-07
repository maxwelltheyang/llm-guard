import logging
from flask import Flask, request
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Set up logging configuration
file_handler = RotatingFileHandler('requests.log', maxBytes=1000000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path}")

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

if __name__ == '__main__':
    app.run(debug=True)
