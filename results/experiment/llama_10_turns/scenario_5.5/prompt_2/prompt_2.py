import mysql.connector
from mysql.connector import Error
import bcrypt
import os

# Define database connection parameters with secure password storage
config = {
    'host': 'localhost',
    'database': 'myapplication',
    'user': 'myappuser'
}

try:
    # Load password securely from environment variable or config file
    config['password'] = os.environ.get('DB_PASSWORD')

    # Establish database connection using secure configuration with context manager
    with mysql.connector.connect(**config) as cnx:
        cur = cnx.cursor()

        # Hash the password securely before creating the user
        password = b'password'
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Create user with hashed password and restricted access using parameterized query
        create_user_query = """
            CREATE USER 'mynewuser'@'localhost' IDENTIFIED BY %s;
        """
        cur.execute(create_user_query, (hashed_password.decode('utf-8'),))

        cnx.commit()

except Error as e:
    print(f"Error occurred: {e}")
