import logging
import sys

# Configure logging to use a secure format and handler
logging.basicConfig(
    level=logging.INFO,  # Set log level (optional)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Secure format
    handlers=[
        logging.StreamHandler(sys.stdout),  # Use stdout for output
        logging.FileHandler('app.log')  # Log to a file
    ]
)

# Example usage of the logger
logging.info("This is an info message.")
logging.error("This is an error message.")
