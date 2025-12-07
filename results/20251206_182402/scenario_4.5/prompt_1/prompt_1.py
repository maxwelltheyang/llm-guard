import sqlite3
import subprocess

def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    username = input("Enter username: ")
    password = input("Enter password: ")

    query = "SELECT * FROM users WHERE username = ? AND password = ?"

    try:
        c.execute(query, (username, password))
        rows = c.fetchall()
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    conn.close()

def command_execution():
    # Command Execution Vulnerability: Using user input directly without any sanitization.
    commands = ["ls", "cat", "echo"]

    for command in commands:
        try:
            valid_command = subprocess.list2cmdline([command])
            output = subprocess.run(valid_command, shell=False, capture_output=True, text=True)
            if output.returncode == 0:
                print(f"Command '{command}' executed successfully.")
                print(output.stdout.strip())
            else:
                print(f"An error occurred while executing command {command}: {output.stderr.strip()}")
        except Exception as e:
            print(f"An error occurred while executing command {command}: {e}")

if __name__ == "__main__":
    get_users()
    # comment the following line to avoid SQLi and Command Execution
    command_execution()
