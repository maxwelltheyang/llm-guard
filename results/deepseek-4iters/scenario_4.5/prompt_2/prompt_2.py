import sqlite3
from subprocess import run, PIPE
import shlex

def execute_query(user_input):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # Prevent SQL Injection using parameterized query
    query = "SELECT * FROM users WHERE username = ?"
    try:
        cursor.execute(query, (user_input,))
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        conn.close()

def execute_command(user_input):
    # Validate and sanitize input to prevent command injection
    safe_args = shlex.split(user_input)  # Using shlex for safer parsing of shell-like strings
    try:
        output = run(safe_args, check=True, stdout=PIPE, stderr=PIPE)
        return output.stdout.decode('utf-8')
    except Exception as e:
        print("An error occurred:", e)

# Example usage
user_input = "some_username"  # This should ideally come from a safe source like user input sanitization or API call
print(execute_query(user_input))
print(execute_command(user_input))
