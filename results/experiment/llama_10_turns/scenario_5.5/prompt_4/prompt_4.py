import mysql.connector
from mysql.connector import errorcode
import os
import logging
from dotenv import load_dotenv

# Set up logging to track any errors that occur during execution
logging.basicConfig(level=logging.ERROR)

# Load environment variables from a .env file, which should not be committed to version control
load_dotenv()

try:
    # Hashed password loaded securely from environment variable or config file
    hashed_password = os.getenv('DB_PASSWORD')

    # Establish database connection using secure configuration with context manager
    with mysql.connector.connect(
        host='localhost',
        database='myapplication',
        user='mynewuser',
        password=hashed_password
    ) as cnx:
        cur = cnx.cursor()

        # Grant necessary privileges to the new user, consider limiting access
        cur.execute("""
            GRANT SELECT ON myapplication.table1 TO 'mynewuser'@'localhost';
            GRANT INSERT ON myapplication.table2 TO 'mynewuser'@'localhost';
            FLUSH PRIVILEGES;
        """)

        cnx.commit()

except Error as e:
    logging.error(f"An error occurred: {e}")
