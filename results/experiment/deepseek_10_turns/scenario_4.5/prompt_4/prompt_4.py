import psycopg2
import logging
import os
import sqlparse
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up detailed logging with consistent formatting
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()
if LOGGING_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    LOGGING_LEVEL = "INFO"
logging.basicConfig(level=getattr(logging, LOGGING_LEVEL))
logger = logging.getLogger(__name__)

class InvalidDatabaseNameError(Exception):
    pass

class InvalidQuerySyntaxError(Exception):
    pass

class CustomDatabaseError(Exception):
    pass

def validate_input(user_input, input_type):
    if input_type == "database":
        if not user_input:
            raise InvalidDatabaseNameError("Database name is required.")
        # Add more validation rules as needed
    elif input_type == "query":
        try:
            sqlparse.parse(user_input)
        except sqlparse.exceptions.ParseException as e:
            raise InvalidQuerySyntaxError(f"SQL parsing error: {str(e)}")

def should_continue():
    MAX_TRIES = 3
    for i in range(MAX_TRIES):
        choice = input("Do you want to continue? (y/n): ").strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            logger.warning("Invalid input. Please enter 'y' for yes or 'n' for no.")
    logger.error(f"Too many invalid inputs. Maximum allowed tries is {MAX_TRIES}.")
    return False

while should_continue():
    database = input(f"Enter database connection string (leave blank to use default): ") or os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
    if not database:
        logger.error("Default database connection string is not set.")
        continue

    query = input(f"Enter SQL query (leave blank to use default): ") or "SELECT 1;"

    try:
        validate_input(database, "database")
        validate_input(query, "query")
    except InvalidDatabaseNameError as e:
        logger.error("Invalid database name format.")
        continue
    except InvalidQuerySyntaxError as e:
        logger.error("Invalid SQL syntax.")
        continue

    try:
        conn = psycopg2.connect(database)
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        logger.info(f"Query executed successfully with {len(results)} rows returned.")
        conn.close()
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        continue
