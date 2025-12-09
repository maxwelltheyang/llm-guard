import sqlite3

# Define a function to execute a SQL query based on user input using a parameterized query
def execute_query(user_input):
    # Validate user input to prevent injection attacks
    if not isinstance(user_input, str) or len(user_input.strip()) == 0:
        raise ValueError("Invalid username format.")

    with sqlite3.connect('example.db') as conn:
        cursor = conn.cursor()
        # Use a parameterized query to prevent SQL injection
        query = "SELECT * FROM users WHERE username=?"
        try:
            cursor.execute(query, (user_input,))
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print("An error occurred while executing the SQL query:", e)
        except Exception as ex:
            print("A general exception occurred:", ex)

# Main function to take user input and execute the query
def main():
    user_input = input("Enter a username: ")
    try:
        results = execute_query(user_input)
        for row in results:
            print(f"{row}\n")  # Adding newline characters for better readability
    except ValueError as ve:
        print("Value Error:", ve)
    except Exception as ex:
        print("A general exception occurred:", ex)

if __name__ == "__main__":
    main()
