import sqlite3
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)

def validate_input(user_input, pattern, input_type):
    if not isinstance(user_input, str):
        raise ValueError(f"{input_type} must be a string.")
    if len(user_input) == 0:
        raise ValueError(f"{input_type} cannot be empty.")
    if pattern and re.search(pattern, user_input, re.IGNORECASE):
        raise ValueError(f"Invalid keyword detected in {input_type}.")

def execute_query(database, query):
    try:
        validate_input(database, None, "database")  # No pattern for database name
        validate_input(query, re.compile(r"^(?!.*(ALTER|CREATE|DELETE|DROP|EXEC|INSERT|SELECT|UPDATE)\b).*$", re.IGNORECASE), "query")

        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        logging.info("Query executed successfully.")
        return results
    except sqlite3.Error as e:
        logging.error(f"An error occurred while executing the query: {e}")
        return []
    except ValueError as ve:
        logging.error(ve)
        return []

def main():
    database = input("Enter the database name: ")
    query = input("Enter your SQL query: ")

    try:
        validate_input(database, None, "database")  # No pattern for database name
        validate_input(query, re.compile(r"^(?!.*(ALTER|CREATE|DELETE|DROP|EXEC|INSERT|SELECT|UPDATE)\b).*$", re.IGNORECASE), "query")
    except ValueError as ve:
        logging.warning(ve)
        return

    results = execute_query(database, query)
    for row in results:
        print(row)

if __name__ == "__main__":
    main()
