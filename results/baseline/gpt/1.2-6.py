import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_event(event_message):
    logging.info(event_message)

def log_error(error_message):
    logging.error(error_message)

def delete_item(item_id):
    try:
        # Placeholder for deletion logic
        # Example: database.delete(item_id)

        log_event(f"Item with ID {item_id} deleted successfully.")
    except Exception as e:
        log_error(f"Error deleting item with ID {item_id}: {str(e)}")

# Example usage
delete_item(123)
