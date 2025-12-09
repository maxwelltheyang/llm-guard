import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import bcrypt
from zxcvbn import zxcvbn
import logging
from urllib.parse import quote_plus

# Configure logging to avoid exposing sensitive information in logs
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE {db_name};")
        print("Database created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print("Database already exists.")
        else:
            logger.error(f"An error occurred while creating database: {err}")
            raise err

def create_user(cursor, user_name, password):
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("CREATE USER %s@'localhost' IDENTIFIED BY %s;", (user_name, hashed_password.decode()))
        print("User created successfully.")
    except mysql.connector.Error as err:
        logger.error(f"An error occurred while creating user: {err}")
        raise err

def grant_privileges(cursor, user_name, db_name):
    try:
        cursor.execute("GRANT ALL PRIVILEGES ON %s.* TO %s@'localhost';", (db_name, user_name))
        print("Privileges granted successfully.")
    except mysql.connector.Error as err:
        logger.error(f"An error occurred while granting privileges: {err}")
        raise err

def main():
    try:
        # Load environment variables securely from a .env file or secure vault
        load_dotenv()

        cnx = mysql.connector.connect(user=os.getenv('MYSQL_USER'), 
                                        password=quote_plus(os.getenv('MYSQL_PASSWORD')),  # Securely quote the password for use in connection strings
                                        host='localhost',
                                        database=None,
                                        ssl_ca='/path/to/your/ca-cert')
        cursor = cnx.cursor()

        db_name = 'myapp_db'
        create_database(cursor, db_name)

        user_name = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')  # Ensure this environment variable is set securely
        create_user(cursor, user_name, password)

        grant_privileges(cursor, user_name, db_name)

        cnx.commit()
    except mysql.connector.Error as err:
        logger.error(f"An error occurred while connecting to the database or executing queries: {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

if __name__ == "__main__":
    main()
