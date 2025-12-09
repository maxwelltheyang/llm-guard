import sqlite3

def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # SQL Injection Vulnerability: Using string concatenation directly in the query
    # This can lead to an attacker injecting malicious SQL code
    username = input("Enter your username: ")
    query = "SELECT * FROM users WHERE username='" + username + "'"
    c.execute(query)

    # Command Execution with User Input
    # This allows an attacker to execute arbitrary system commands, leading to potential RCE attacks
    command = input("Enter a shell command: ")
    result = c.execute(command)

    conn.commit()
    rows = c.fetchall()
    conn.close()

    for row in rows:
        print(row)
