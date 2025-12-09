import mysql.connector
from mysql.connector import errorcode
import os
import secrets
import string

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
        # Use a more robust method to generate a secure password
        password = get_secure_password()
    try:
        cursor.execute(f"CREATE USER '{user}'@'localhost' IDENTIFIED BY '{password}'")
        print("User created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating user: {err}")
        raise err

def get_secure_password():
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(secrets.choice(alphabet) for i in range(32))  # Adjust length as needed
    return password

def main():
    try:
        cnx = mysql.connector.connect(user='root', password=os.getenv('DB_ROOT_PASSWORD'))
        cursor = cnx.cursor()

        create_database(cursor)
        create_user(cursor)

        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(f"Error connecting to the database or performing operations: {err}")
        raise err

if __name__ == "__main__":
    main()
