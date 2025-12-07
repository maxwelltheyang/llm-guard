import logging

# Create a logger object
logger = logging.getLogger(__name__)

# Set the logging level to DEBUG ( lowest level )
logging.basicConfig(level=logging.DEBUG)

# Define a custom format for log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a console handler and attach the formatter
ch = logging.StreamHandler()
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

try:
    # Simulate some code that may raise an exception
    x = 1 / 0
except Exception as e:
    # Log the exception at ERROR level
    logger.error(f"An error occurred: {str(e)}")
