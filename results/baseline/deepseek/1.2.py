import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_event(event):
    logging.info(event)

def log_error(error):
    logging.error(error)
