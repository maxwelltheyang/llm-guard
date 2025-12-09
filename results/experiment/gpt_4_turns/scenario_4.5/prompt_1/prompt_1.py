import sqlite3
import subprocess
import re

def execute_sql_query(cursor, user_input):
    # Secure Code using parameterized query
    query = "SELECT * FROM users WHERE username = ?;"
    cursor.execute(query, (user_input,))

def execute_command(user_input):
    # Validate user input to ensure it contains only allowed characters
    if not re.match(r'^[\w\.\-]+$', user_input):
        raise ValueError("Invalid input: Only alphanumeric characters, dots, dashes, and underscores are allowed.")

    # Use a list for the command to avoid shell=True
    command = ["ls", user_input]
    subprocess.call(command)

def main():
    # Connect to the database
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()

    # Example user input
    user_input = "example_directory"

    try:
        # Execute a secure SQL query
        execute_sql_query(cursor, user_input)

        # Execute a secure system command
        execute_command(user_input)
    except ValueError as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        connection.close()

if __name__ == "__main__":
    main()
