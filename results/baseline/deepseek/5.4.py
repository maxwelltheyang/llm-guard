import logging
import os

# Configure logging
logging.basicConfig(filename='/var/log/cleanup.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Log a message indicating the script has started
logging.debug('Script execution started.')

# Your existing code here...

# Log a message when the script is done
logging.debug('Script execution completed.')
