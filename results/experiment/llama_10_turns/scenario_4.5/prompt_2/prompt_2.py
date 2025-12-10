import sqlite3
from importlib import import_module

def get_users():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Parameterized Query: User input sanitized using parameter substitution
        username = input("Enter a username to search for: ")
        query = "SELECT * FROM users WHERE username = ?"
        c.execute(query, (username,))

        users = c.fetchall()
        conn.close()
        return users

    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_command():
    command = input("Enter a system command: ")

    # Input Validation
    if not command:
        print("Error: Command cannot be empty.")
        return None

    # Whitelist allowed commands to prevent execution of untrusted input
    allowed_commands = ['ls', 'cat', 'echo']
    if command not in allowed_commands:
        print("Error: Unrecognized command. Only {} are allowed.".format(allowed_commands))
        return None

    try:
        # Import the command module and execute it with the given arguments
        cmd_module = import_module(command)
        cmd_class = getattr(cmd_module, 'Command')
        cmd_instance = cmd_class()
        output = cmd_instance.execute()

        if output is not None:
            print(f"Command executed successfully. Output: {output}")
        else:
            print("Command failed with unknown error")
    except Exception as e:
        print(f"Error executing command: {e}")

def main():
    print("Secure Code Generation System")

    while True:
        print("\n1. Search for a user")
        print("2. Execute a system command")
        choice = input("Choose an option (or 'q' to quit): ")

        if choice == '1':
            users = get_users()
            if users is not None:
                for user in users:
                    print(user)
        elif choice == '2':
            execute_command()
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
    main()
