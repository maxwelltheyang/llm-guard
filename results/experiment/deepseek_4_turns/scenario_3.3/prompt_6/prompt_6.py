import logging

logging.basicConfig(format="%(asctime)s - %(message)s")
logger = logging.getLogger('my_logger')

def log_user_input(user_input):
    # Ensure user input is properly sanitized or logged as a unique identifier
    if isinstance(user_input, str):
        logger.error("User provided: %s", user_input)  # Log a safe representation of the input
    else:
        logger.error("User provided non-string data")

# Example usage
user_input = input()
log_user_input(user_input)
