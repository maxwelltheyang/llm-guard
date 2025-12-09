import os
import logging
import mysql.connector
from mysql.connector import errorcode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_config():
    config = {
        'user': os.getenv('DB_USER', ''),
        'password': os.getenv('DB_PASSWORD', ''),
        'host': os.getenv('DB_HOST', ''),
        'ssl_ca': os.getenv('SSL_CA')  # Adding SSL configuration if present
    }
    if os.getenv('DB_DATABASE'):
        config['database'] = os.getenv('DB_DATABASE')
    logging.info(f"Using database configuration: {config}")
    return config

def connect_to_db(config):
    try:
        cnx = mysql.connector.connect(**config)
        logging.info("Connected to the database successfully.")
        return cnx
    except mysql.connector.Error as err:
        logging.error(f"Failed to connect to the database: {err}")
        raise  # Re-raise the exception without SystemExit

def check_database_existence(cnx, db_name):
    cursor = cnx.cursor()
    try:
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        result = cursor.fetchone()
        if result:
            logging.info(f"Database '{db_name}' exists.")
        else:
            logging.warning(f"Database '{db_name}' does not exist.")
    except mysql.connector.Error as err:
        logging.error(f"Error checking database existence: {err}")
        raise  # Re-raise the exception without SystemExit
    finally:
        cursor.close()

def main():
    config = get_db_config()

    missing_vars = [var for var in ['DB_USER', 'DB_PASSWORD', 'DB_HOST'] if os.getenv(var) is None]
    if not missing_vars:  # If the list is empty, all vars are set
        try:
            cnx = mysql.connector.connect(**config)
            logging.info("Connected to the database successfully.")
            db_name = config.get('database', 'information_schema')
            check_database_existence(cnx, db_name)
        except mysql.connector.Error as err:
            logging.error(f"Failed to connect to the database: {err}")
            raise
        except Exception as ex:
            logging.error(f"Unexpected error: {ex}")
            raise
    else:
        missing_vars_str = ', '.join(missing_vars)
        logging.error(f"Missing environment variables: {missing_vars_str}")
        raise EnvironmentError(f"The following environment variables are required but not set: {missing_vars_str}")

if __name__ == "__main__":
    main()
