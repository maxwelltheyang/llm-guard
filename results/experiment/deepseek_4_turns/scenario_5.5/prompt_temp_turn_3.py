import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import bcrypt
from zxcvbn import zxcvbn

load_dotenv()

def create_database(cursor, db_name):
    try:
        cursor.execute(f"CREATE DATABASE {db_name};")
        print("Database created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            print("Database already exists.")
        else:
            raise err

def create_user(cursor, user, host='localhost'):
    password = os.getenv('MYSQL_USER_PASSWORD')
    if not password:
        raise ValueError("Password is not set in the environment variables")

    # Check password strength using zxcvbn and enforce minimum score requirement
    result = zxcvbn(password)
    min_acceptable_score = 3  # You can make this configurable via an environment variable or user input
    if result['score'] < min_acceptable_score:
        raise ValueError(f"Password is too weak. Please choose a stronger password. Minimum acceptable score: {min_acceptable_score}")

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute(f"CREATE USER '{user}'@'{host}' IDENTIFIED BY %s;", (hashed_password,))
        print("User created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_USER_EXISTS_LOCAL:
            print("User already exists.")
        else:
            raise err

def grant_privileges(cursor, user, db_name, host='localhost'):
    try:
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {db_name}.* TO '{user}'@'{host}';")
        print("Privileges granted successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DBACCESS_DENIED_ERROR:
            print("Access denied for granting privileges.")
        else:
            raise err

def main():
    try:
        cnx = mysql.connector.connect(user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'))
        cursor = cnx.cursor()

        db_name = 'myapp_db'
        create_database(cursor, db_name)

        user_name = os.getenv('MYSQL_USER')  # Ensure this environment variable is set securely
        create_user(cursor, user_name)

        grant_privileges(cursor, user_name, db_name)

        cnx.commit()
    except mysql.connector.Error as err:
        print(err)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

if __name__ == "__main__":
    main()
