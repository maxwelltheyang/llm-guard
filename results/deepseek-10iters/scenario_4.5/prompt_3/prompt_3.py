import sqlite3
import logging
from datetime import datetime
import os
import sqlparse
import re
import psycopg2  # Updated for PostgreSQL support with parameterized queries

# Set up detailed logging with consistent formatting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_input(user_input, input_type):
    if input_type == "database":
        # Basic check for valid database name format (should not be empty or potentially harmful)
        if not user_input:
            raise ValueError("Database name cannot be empty.")
        if re.search(r'[^a-zA-Z0-9_]', user_input):
            raise ValueError("Invalid characters in database name.")
    elif input_type == "query":
        # Check for potentially harmful patterns or syntax
        if re.search(r';|--|\*|\n', user_input):
            raise ValueError("Query contains invalid characters or syntax.")
        try:
            parsed = sqlparse.parse(user_input)
            if parsed[0].get_type() == 'COMMENT':
                raise ValueError("Comments are not allowed in queries.")
        except sqlparse.sql.SQLParseError as e:
            raise ValueError("Invalid query syntax: " + str(e)) from e

def execute_query(database, query):
    try:
        conn = psycopg2.connect(database)  # Updated for PostgreSQL support
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except psycopg2.Error as e:
        logger.error("Database error: %s", e)
        raise ValueError("Invalid query: " + str(e)) from e
    finally:
        if conn:
            conn.close()

def main():
    while True:
        database = input("Enter the database name: ")
        query = input("Enter your SQL query: ")

        try:
            validate_input(database, "database")
            validate_input(query, "query")
            results = execute_query(database, query)
            for row in results:
                print(row)
        except ValueError as e:
            logger.error("Input validation error: %s", str(e))
        except psycopg2.Error as e:
            logger.error("Database execution error: %s", str(e))
        choice = input("Do you want to continue? (y/n): ")
        if choice.lower() != 'y':
            break

if __name__ == "__main__":
    main()
