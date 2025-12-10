import mysql.connector
from mysql.connector import Error
import bcrypt
import os
import logging

# Set up logging to track any errors that occur during execution
logging.basicConfig(level=logging.ERROR)

# Define database connection parameters with secure password storage
config = {
    'host': 'localhost',
    'database': 'myapplication',
    'user': 'myappuser'
}

try:
    # Load password securely from environment variable or config file
    password = os.environ.get('DB_PASSWORD')

    # Establish database connection using secure configuration with context manager
    with mysql.connector.connect(**config) as cnx:
        cur = cnx.cursor()

        # Hash the password securely before creating the user (use a strong password and consider enforcing password policies)
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Create user with hashed password and restricted access using parameterized query
        cur.execute("CREATE USER 'mynewuser'@'localhost' IDENTIFIED BY %s;" , (hashed_password.decode('utf-8'),))

        cnx.commit()

except Error as e:
    logging.error(f"An error occurred: {e}")
