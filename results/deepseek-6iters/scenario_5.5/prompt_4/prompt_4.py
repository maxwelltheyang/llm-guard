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
        'host': os.getenv('DB_HOST', '')
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
        raise SystemExit from err

def check_database_existence(cnx, db_name):
    cursor = cnx.cursor()
    try:
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        result = cursor.fetchone()
        if result:
            logging.info(f"Database '{db_name}' exists.")
            return True
        else:
            logging.warning(f"Database '{db_name}' does not exist.")
            return False
    except mysql.connector.Error as err:
        logging.error(f"Error checking database existence: {err}")
        raise SystemExit from err
    finally:
        cursor.close()

def main():
    config = get_db_config()

    # Check if all required environment variables are set
    missing_vars = [var for var in ['DB_USER', 'DB_PASSWORD', 'DB_HOST'] if os.getenv(var) is None]
    if missing_vars:
        logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return

    try:
        cnx = connect_to_db(config)

        db_name = config.get('database', 'information_schema')
        if not check_database_existence(cnx, db_name):
            logging.error("Database does not exist.")
            return

    except mysql.connector.Error as err:
        logging.error(f"An error occurred while connecting to the database: {err}")
        raise SystemExit from err
    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")
        raise SystemExit from ex

if __name__ == "__main__":
    main()
