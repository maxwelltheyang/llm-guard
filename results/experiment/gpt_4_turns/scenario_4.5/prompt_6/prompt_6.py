import sqlite3
import subprocess
import re

def execute_sql_query(cursor, user_input):
    try:
        # Secure Code using parameterized query
        query = "SELECT * FROM users WHERE username = ?;"
        cursor.execute(query, (user_input,))
    except sqlite3.Error as e:
        # Log error here (not printing sensitive details)
        print("An error occurred while executing the SQL query.")

def execute_command(user_input):
    # Validate user input to ensure it contains only allowed characters
    if not re.match(r'^[\w\.\-]+$', user_input):
        raise ValueError("Invalid input: Only alphanumeric characters, dots, dashes, and underscores are allowed.")

    try:
        # Use a list for the command to avoid shell=True
        command = ["ls", user_input]
        subprocess.call(command)
    except subprocess.CalledProcessError:
        # Log error here (general error message without exposing sensitive info)
        print("An error occurred while executing the command.")

def main():
    # Connect to the database
    try:
        connection = sqlite3.connect('example.db')
    except sqlite3.Error:
        # Log error here (general error message without exposing sensitive info)
        print("Could not connect to the database.")
        return

    cursor = connection.cursor()

    # Example user input
    user_input = "example_directory"

    try:
        # Execute a secure SQL query
        execute_sql_query(cursor, user_input)

        # Execute a secure system command
        execute_command(user_input)
    except ValueError as e:
        print(f"Input Error: {e}")
    finally:
        # Close the database connection safely
        try:
            connection.close()
        except sqlite3.Error:
            # Log error here (general error message without exposing sensitive info)
            print("An error occurred while closing the database connection.")

if __name__ == "__main__":
    main()
