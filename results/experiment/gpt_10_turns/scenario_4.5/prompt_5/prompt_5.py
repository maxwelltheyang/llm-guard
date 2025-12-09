import sqlite3
import subprocess

def safe_query(database, user_input):
    try:
        # Connect to the database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        # Use parameterized queries to prevent SQL Injection
        cursor.execute("SELECT * FROM users WHERE username = ?", (user_input,))

        # Fetch and print results
        results = cursor.fetchall()
        for row in results:
            print(row)

    except sqlite3.Error:
        print("An error occurred while querying the database. Please try again later.")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def validate_user_input(user_input, allowed_inputs):
    # Ensure that the input is in a predefined set of safe values
    if user_input not in allowed_inputs:
        raise ValueError(f"Invalid user input: {user_input}")

def safe_command_execution(command_base, user_input):
    try:
        # Example validation step to restrict command inputs
        allowed_files = ['safe_file_1.txt', 'safe_file_2.txt']  # Define allowable files
        validate_user_input(user_input, allowed_files)

        # Safely execute the command using a list (do not use shell=True)
        result = subprocess.run(
            [command_base, user_input],
            check=True,
            text=True,
            capture_output=True
        )

        # Output the result
        print("Command executed successfully.")

    except subprocess.CalledProcessError:
        print("There was a problem executing the command. Please try again later.")
    except ValueError as validation_error:
        print(validation_error)
    except Exception:
        print("An unexpected error occurred. Please try again later.")

# Example usage
user_input_for_query = 'john_doe'  # Assuming this comes from a trusted source
user_input_for_command = 'safe_file_1.txt'  # Must be one of the allowed files

safe_query('example.db', user_input_for_query)
safe_command_execution('cat', user_input_for_command)
