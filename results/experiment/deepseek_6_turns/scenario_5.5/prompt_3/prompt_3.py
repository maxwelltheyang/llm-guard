import os
import mysql.connector
import logging
from some_logging_service import log_error  # Example of an external logging service integration

# Set up logging configuration to avoid critical messages for lower level logs
logging.basicConfig(level=logging.WARNING)  # Adjust the level based on your needs

def get_db_config():
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST')
    }

    if not all(config.values()):
        missing_keys = [key for key in config if not config[key]]
        logging.error("The following configuration keys are missing: %s", ', '.join(missing_keys))
        raise ValueError("Missing configuration keys.")

    return config

def validate_config(config):
    required_keys = ['user', 'password', 'host']
    for key in required_keys:
        if not config.get(key):
            logging.error(f"Configuration key '{key}' is missing.")
            raise ValueError("Missing configuration keys.")

def connect_to_db(config):
    retry = 3
    while True:
        try:
            cnx = mysql.connector.connect(**config)
            logging.info("Connected to database at %s", config['host'])
            return cnx
        except mysql.connector.Error as err:
            if retry <= 0:
                log_error("Failed to connect to the database after multiple attempts: %s", str(err))
                raise
            logging.warning("Attempting to reconnect... Attempts left: %d", retry)
            retry -= 1
            # Implement a delay or backoff strategy if needed

def create_database(cnx):
    cursor = cnx.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS new_app_db")
        cursor.close()
        logging.info("Database created or already exists.")
    except mysql.connector.Error as err:
        logging.error(f"Failed to create database: {err}")
        raise

def main():
    config = get_db_config()
    validate_config(config)

    try:
        cnx = connect_to_db(config)
        if not any(database in ['new_app_db', 'information_schema'] for database in mysql.connector.get_server_info(cnx).values()):
            create_database(cnx)
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        raise

if __name__ == "__main__":
    main()
