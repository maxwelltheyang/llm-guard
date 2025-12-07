import sqlite3

def query_database(user_input):
    try:
        conn = sqlite3.connect('example.db')
        cursor = conn.cursor()

        # Using parameterized queries to prevent SQL injection
        cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))

        results = cursor.fetchall()
        return results

    except sqlite3.Error:
        # Log the error or handle it
        raise

    finally:
        conn.close()

# Example usage:
# result = query_database("Alice")
