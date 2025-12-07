import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def audit_log(event):
    logging.info(event)

# Example usage
try:
    1/0  # This will raise a ZeroDivisionError
except Exception as e:
    error_msg = str(e)
    audit_log(f"An error occurred: {error_msg}")
