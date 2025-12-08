import logging

def logError(self, message, *args):
    try:
        self.logger.error(message % args)
    except TypeError as e:
        self.logger.error(f"Error formatting error message: {e}")
        self.logger.error(message)

class Logger:
    def __init__(self, logger):
        self.logger = logger

# Example usage
logger = logging.getLogger()
logError(logger, "Error code: %d", 123)
