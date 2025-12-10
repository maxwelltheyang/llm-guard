import sqlite3
import importlib.util
from pathlib import Path
import logging
import os
import shlex
import re

logging.basicConfig(level=logging.INFO)

# Define the full path to the database file
DB_FILE_PATH = '/path/to/users.db'

def get_users():
    try:
        conn = sqlite3.connect(DB_FILE_PATH)
        c = conn.cursor()

        # Parameterized Query: User input sanitized using parameter substitution
        username = input("Enter a username to search for (lowercase, mixed case or uppercase): ")

        if len(username.strip()) == 0:
            raise ValueError("Username cannot be empty.")

        valid_chars = re.compile(r'^[a-zA-Z0-9._-]+$')
        if not valid_chars.search(username):
            raise ValueError("Invalid username. Only alphanumeric characters, dots, and underscores are allowed.")

        c.execute("SELECT * FROM users WHERE username = ?", (username,))

        results = c.fetchone()

        if results is not None:
            print(results)
        else:
            print("Username not found in database.")

        conn.close()
    except sqlite3.Error as e:
        logging.error(f"SQLite error occurred while retrieving user: {str(e)}")
    except ValueError as e:
        print(f"Error: {str(e)}")

def load_module_from_file(module_name):
    try:
        module_spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")

        if module_spec is None:
            raise ImportError(f"No module named '{module_name}' found.")

        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        return module
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        print(f"Error: The module requires the '{str(e)}' dependency. Please install it using pip (e.g., `pip install {module_name}`) and try again.")
    except Exception as e:
        logging.error(f"Exception occurred while loading module: {str(e)}")
        print(f"Error: An unexpected error occurred. Please check the module's code for errors.")

def validate_command_name(cmd_name):
    pattern = r'^[a-zA-Z0-9_.-]+\.py$'
    if re.match(pattern, cmd_name, re.IGNORECASE):
        return True
    else:
        raise ValueError("Invalid command name. Please enter a valid Python file name with a .py extension.")

def main():
    while True:
        try:
            choice = input("Enter '1' to retrieve a user, '2' to execute a module, or 'q' to quit: ")

            if choice.lower() not in ['1', '2', 'q']:
                print("Invalid choice. Please choose a valid option.")
                continue

            if choice == '1':
                get_users()
            elif choice.lower() == 'q':
                break
            else:
                cmd_name = input("Enter the command name (e.g., ExampleModule.py): ")

                try:
                    validate_command_name(cmd_name)
                except ValueError as e:
                    print(str(e))
                    continue

                module = load_module_from_file(cmd_name[:-3])

                if hasattr(module, 'execute'):
                    try:
                        module.execute()
                    except Exception as e:
                        logging.error(f"Exception occurred while executing module: {str(e)}")
                        print(f"Error: An unexpected error occurred. Please check the module's code for errors.")
                else:
                    print("Module does not have an execute method.")
        except KeyboardInterrupt as e:
            print("\nProgram interrupted by user.")
            break

if __name__ == "__main__":
    main()
