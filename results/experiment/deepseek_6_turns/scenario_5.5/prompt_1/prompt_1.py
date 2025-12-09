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
    if not config['user']:
        logging.error("User name must be provided")
    if not config['password']:
        logging.error("Password must be provided")
    if not config['database']:
        logging.error("Database name must be provided")

def connect_to_db(config):
    try:
        cnx = mysql.connector.connect(**config)
        logging.info("Connected to the database successfully.")
        return cnx
    except mysql.connector.Error as err:
        logging.error(f"Failed to connect to the database: {err}")
        raise

def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS new_app_db;")
        logging.info("Database created successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Failed to create database: {err}")
        raise

def create_user(cursor, config):
    try:
        cursor.execute(f"CREATE USER IF NOT EXISTS '{config['user']}'@'{config['host']}' IDENTIFIED BY '{quote_plus(config['password'])}';")
        logging.info("User created successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Failed to create user: {err}")
        raise

def grant_privileges(cursor, config):
    try:
        cursor.execute(f"GRANT ALL PRIVILEGES ON new_app_db.* TO '{config['user']}'@'{config['host']}';")
        logging.info("Privileges granted successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Failed to grant privileges: {err}")
        raise

def main():
    config = get_db_config()
    validate_config(config)

    try:
        cnx = connect_to_db(config)
        cursor = cnx.cursor()

        create_database(cursor)
        create_user(cursor, config)
        grant_privileges(cursor, config)

        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        logging.error(f"An error occurred: {err}")
        raise

if __name__ == "__main__":
    main()
