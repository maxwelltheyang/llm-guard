import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

def load_ssh_private_key(file_path):
    try:
        with open(file_path, 'r') as file:
            key_data = file.read()
        return key_data
    except Exception as e:
        logging.error("Failed to load SSH private key.")
        raise e

private_key_path = 'path/to/private_key'
try:
    # Load the SSH private key (not logged)
    private_key = load_ssh_private_key(private_key_path)
    logging.info("SSH private key loaded successfully.")
except Exception as e:
    logging.error("An error occurred while loading the SSH private key.")
