import sqlite3

# Define a function to execute a SQL query based on user input using a parameterized query
def execute_query(user_input):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    # Use a parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE username=?"
    try:
        cursor.execute(query, (user_input,))
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        conn.close()

# Main function to take user input and execute the query
def main():
    user_input = input("Enter a username: ")
    results = execute_query(user_input)
    for row in results:
        print(f"{row}\n")  # Adding newline characters for better readability

if __name__ == "__main__":
    main()
