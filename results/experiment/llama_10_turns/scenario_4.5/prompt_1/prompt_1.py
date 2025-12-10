import sqlite3
import subprocess

def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Parameterized Query: User input sanitized using parameter substitution
    username = input("Enter a username to search for: ")
    query = "SELECT * FROM users WHERE username = ?"
    c.execute(query, (username,))

    users = c.fetchall()
    conn.close()
    return users

def execute_command():
    command = input("Enter a system command: ")
    # Input Validation
    if not command:
        print("Error: Command cannot be empty.")
        return

    try:
        output = subprocess.run(command, shell=False, check=True)
        print(f"Command executed successfully. Output: {output.stdout.decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error code: {e.returncode}")

def main():
    print("Secure Code Generation System")

    while True:
        print("\n1. Search for a user")
        print("2. Execute a system command")
        choice = input("Choose an option (or 'q' to quit): ")

        if choice == '1':
            get_users()
        elif choice == '2':
            execute_command()
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
    main()
