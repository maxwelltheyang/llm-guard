import os
import mysql.connector
import logging
from urllib.parse import quote_plus

# Configure logging for error handling
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_config():
    return {
        'user': os.getenv('DB_USER', 'new_app_user'),
        'password': os.getenv('DB_PASSWORD', 'secure_pass123'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'new_app_db')
    }

def validate_config(config):
    if not config['user'] or not config['password']:
        logging.critical("User and password must be provided.")
        raise ValueError("User and password must be provided.")
    if not config.get('host'):
        logging.critical("Host must be provided.")
        raise ValueError("Host must be provided.")
    if not config.get('database'):
        logging.critical("Database name must be provided.")
        raise ValueError("Database name must be provided.")

def connect_to_db(config):
    try:
        cnx = mysql.connector.connect(**config)
        logging.info("Connected to database at %s", config['host'])
        return cnx
    except mysql.connector.Error as err:
        logging.error("Failed to connect to the database: %s", err)
        raise

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
        create_database(cnx)
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        raise

if __name__ == "__main__":
    main()
