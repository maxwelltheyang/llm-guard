import logging
from logging.handlers import RotatingFileHandler
import os
import json

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a rotating file handler
file_handler = RotatingFileHandler('audit.log', maxBytes=1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)

# Create a stream handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)

# Create a formatter and attach it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def audit_log(event):
    try:
        json.dump(event, open('audit.log', 'a'))
    except Exception as e:
        logger.error(f"Error logging event: {e}")

def delete_item(item_id):
    # Simulate a database deletion
    print(f"Deleting item with id {item_id}")

    try:
        # Deletion code here
        pass
    except Exception as e:
        audit_log({
            'event': 'delete',
            'item_id': item_id,
            'error': str(e)
        })
        logger.error(f"Error deleting item: {e}")

# Test the audit log and deletion function
audit_log({'event': 'delete', 'item_id': 1})
delete_item(2)
