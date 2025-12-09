import sqlite3
import logging

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_input(user_input, input_type):
    if not isinstance(user_input, str):
        logger.error(f"{input_type} must be a string.")
        raise ValueError(f"{input_type} must be a string.")
    if len(user_input) == 0:
        logger.error(f"{input_type} cannot be empty.")
        raise ValueError(f"{input_type} cannot be empty.")

def execute_query(database, query, params=None):
    validate_input(database, "database")
    validate_input(query, "query")

    try:
        with sqlite3.connect(database) as conn:  # Use the with statement for connection management
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)  # Use parameterized query with named placeholders
            else:
                cursor.execute(query)
            results = cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"SQL Error: {e}")
        raise

    logging.info("Query executed successfully.")
    return results

def main():
    database = input("Enter the database name: ")
    query = input("Enter your SQL query: ")

    try:
        validate_input(database, "database")
        validate_input(query, "query")
    except ValueError as ve:
        logger.error(str(ve))
        return

    results = execute_query(database, query)  # Pass the query and parameters separately
    for row in results:
        print(row)

if __name__ == "__main__":
    main()
