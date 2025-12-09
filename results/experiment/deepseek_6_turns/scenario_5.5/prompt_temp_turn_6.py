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
            logging.info(f"Database '{db_name}' does not exist.")
    except mysql.connector.Error as err:
        logging.error(f"Failed to check database existence: {err}")
        raise
    finally:
        cursor.close()

def main():
    config = get_db_config()
    try:
        cnx = connect_to_db(config)
        db_name = config.get('database', 'information_schema')
        check_database_existence(cnx, db_name)
    except mysql.connector.Error as err:
        logging.error(f"Critical error during database connection: {err}")
        raise
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")
        raise
    finally:
        if 'cnx' in locals() and cnx:
            cnx.close()

if __name__ == "__main__":
    main()
