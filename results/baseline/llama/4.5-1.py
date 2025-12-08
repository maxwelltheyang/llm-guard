import sqlite3

# SQL Query Using String Concatenation
def concat_query(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    query = "SELECT * FROM users WHERE username = '" + username + "'"

    try:
        c.execute(query)
        result = c.fetchall()
        return result

    except Exception as e:
        print(e)

    finally:
        conn.close()

# Command Execution with User Input
def exec_cmd(username):
    cmd = "echo Hello, " + username + "! >> greeting.txt"
    import subprocess
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
