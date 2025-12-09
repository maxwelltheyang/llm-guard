import mysql.connector
from mysql.connector import errorcode
import os

# Database connection setup with parameter for credentials
def get_db_connection(user, password, host='localhost', database='mydatabase'):
    try:
        conn = mysql.connector.connect(user=user, password=password, host=host, database=database)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

# Updated registerUser function to accept parameters for username and password
def registerUser(username, password):
    conn = get_db_connection(user=os.getenv('DB_USER'), password=password)
    if conn is not None:
        try:
            # Your registration logic here
            pass
        finally:
            conn.close()

# Example usage of registerUser function with environment variables for credentials
if __name__ == "__main__":
    registerUser(username="exampleuser", password=os.getenv('DB_PASSWORD'))
