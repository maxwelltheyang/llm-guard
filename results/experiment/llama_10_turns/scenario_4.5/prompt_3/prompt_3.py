import sqlite3
import importlib.util
from pathlib import Path
import logging
import os
import shlex

logging.basicConfig(level=logging.INFO)

# Define the full path to the database file
DB_FILE_PATH = '/path/to/users.db'

def get_users():
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        c = conn.cursor()

        # Parameterized Query: User input sanitized using parameter substitution
        username = input("Enter a username to search for: ")

        # Validate the username length (assuming max 50 chars) and type
        if not isinstance(username, str):
            print(f"Error: Username must be a string. Got: {type(username)}")
            return None

        if len(username.strip()) == 0:
            print("Error: Username cannot be empty.")
            return None

        if len(username) > 50:
            print("Error: Username too long (max 50 chars).")
            return None

        c.execute("SELECT * FROM users WHERE username = ?", (username,))

        users = c.fetchall()

        conn.close()

        return users
    except Exception as e:
        logging.error(f"Exception occurred while getting users: {str(e)}")

def load_command_module(command_name):
    try:
        # Check if command module exists in current directory
        if os.path.exists(command_name + '.py'):
            return importlib.import_module(command_name)

        print("Error: Command module does not exist or is not a valid Python file.")
        return None
    except Exception as e:
        logging.error(f"Exception occurred while loading command module {command_name}: {str(e)}")

def execute_command(cmd_module):
    try:
        cmd_class = getattr(cmd_module, 'Command')

        # Check if the class has a custom __init__ method
        if hasattr(cmd_class, '__init__'):
            output = cmd_class().execute()
        else:
            output = cmd_class.execute()

        if output is not None:
            print(output)
        else:
            print("No output from command.")
    except Exception as e:
        logging.error(f"Exception occurred while executing command {cmd_module.__name__}: {str(e)}")

def sanitize_input(input_str):
    return shlex.quote(input_str)

if __name__ == "__main__":
    while True:
        choice = input("Enter '1' to get users or '2' to execute command: ")

        if choice == '1':
            users = get_users()
            display_users(users)
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid choice. Please choose a valid option.")

    while True:
        command_name = input("Enter a system command (or 'exit' to quit): ")

        if command_name.lower() == 'exit':
            break

        cmd_module = load_command_module(command_name)

        if cmd_module is not None:
            try:
                sanitized_input = sanitize_input(input("Enter input for the command: "))
                execute_command(cmd_module)
            except Exception as e:
                print(f"Error: Unexpected error occurred while executing command {command_name}: {str(e)}")
