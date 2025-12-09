import os
import sqlite3
import subprocess

def execute_secure_query(db_connection, user_input):
    try:
        # Prepared statement to prevent SQL injection
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))
        results = cursor.fetchall()
        for row in results:
            print(row)
    except sqlite3.Error as e:
        # Log the error if needed but avoid exposing sensitive information
        print("A database error occurred.")
    finally:
        cursor.close()

def sanitize_path(input_path):
    # Allow only absolute paths and verify they start with allowed directories
    allowed_dirs = ['/usr/bin', '/usr/local/bin']
    input_path = os.path.abspath(input_path)

    if any(input_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
        return input_path
    else:
        raise ValueError("Invalid path provided.")

def execute_secure_command(user_input):
    try:
        # Validate the path using a whitelist for safety
        safe_path = sanitize_path(user_input)
        # Use subprocess.run with validated, safe_path
        result = subprocess.run(["ls", "-l", safe_path], capture_output=True, text=True)
        print(result.stdout)
    except ValueError as ve:
        # Log value errors with caution to avoid leaking path information
        print("Input validation error.")
    except subprocess.SubprocessError as e:
        # General error handling without exposing sensitive command information
        print("An error occurred while executing the command.")

def main():
    # Connect to SQLite database (example)
    db_connection = sqlite3.connect('example.db')

    # Example user input
    user_input_sql = 'john_doe'
    user_input_cmd = '/usr/bin'

    # Execute functions
    execute_secure_query(db_connection, user_input_sql)
    execute_secure_command(user_input_cmd)

    # Close the database connection
    db_connection.close()

if __name__ == "__main__":
    main()
