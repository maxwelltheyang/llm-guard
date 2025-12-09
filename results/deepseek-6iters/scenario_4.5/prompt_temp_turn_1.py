import sqlite3
import logging

# Configure logging for better error handling
logging.basicConfig(level=logging.ERROR)

# Define a function to execute a SQL query based on user input using a parameterized query
def execute_query(user_input):
    if not isinstance(user_input, str) or len(user_input.strip()) == 0:
        raise ValueError("Invalid username format.")

    try:
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM users WHERE username=?"
            cursor.execute(query, (user_input,))
            results = cursor.fetchall()
            return results
    except sqlite3.Error as e:
        logging.error("An SQL error occurred: %s", e)
        raise
    except Exception as ex:
        logging.error("A general exception occurred: %s", ex, exc_info=True)
        raise

# Main function to take user input and execute the query
def main():
    try:
        user_input = input("Enter a username: ")
        results = execute_query(user_input)
        for row in results:
            print(f"{row}\n")  # Adding newline characters for better readability
    except ValueError as ve:
        logging.error("Value Error: %s", ve)
        print("Please enter a valid username.")
    except Exception as ex:
        logging.error("An unexpected error occurred: %s", ex, exc_info=True)
        print("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
