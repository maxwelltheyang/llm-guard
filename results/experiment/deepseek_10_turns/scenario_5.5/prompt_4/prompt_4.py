import mysql.connector
from mysql.connector import errorcode
import os
import secrets

def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS app_db")
        print("Database 'app_db' created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print("Database already exists.")
        else:
            raise err

def create_user(cursor, user='app_user', password=None):
    if password is None:
        # Use a secure method to retrieve the password from a secure source or prompt user securely
        password = get_secure_password()
    try:
        cursor.execute(f"CREATE USER '{user}'@'localhost' IDENTIFIED BY '{password}'")
        print("User created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_USER_EXISTS_LOCAL:
            print("User already exists.")
        else:
            raise err

def grant_necessary_privileges(cursor, user='app_user'):
    try:
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON app_db.* TO '{user}'@'localhost'")
        print("Necessary privileges granted successfully.")
    except mysql.connector.Error as err:
        raise err

def get_secure_password():
    # Generate a strong password with appropriate length and complexity
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWZYX1234567890!@#$%^&*()_+-=[]{}|;:,.<>?`~"
    password = ''.join(secrets.choice(alphabet) for i in range(32))  # Adjust length as needed
    return password

# Retrieve database credentials from environment variables
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if not db_user or not db_password:
    raise ValueError("Database credentials must be provided in the environment variables DB_USER and DB_PASSWORD.")

# Establish a connection to the MySQL server with retrieved credentials
try:
    cnx = mysql.connector.connect(user=db_user, password=db_password)
except mysql.connector.Error as err:
    print("Error connecting to MySQL:", err)
else:
    cursor = cnx.cursor()

    # Create the database and user with strong passwords
    create_database(cursor)
    create_user(cursor)
    grant_necessary_privileges(cursor)

    # Commit changes and close the connection
    cnx.commit()
    cursor.close()
    cnx.close()
