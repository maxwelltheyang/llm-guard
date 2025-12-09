import os
import logging
from dotenv import load_dotenv
from psycopg2 import connect, Error
from sqlparse.sql import parse

# Load environment variables from .env file
load_dotenv()

# Set up detailed logging with consistent formatting
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()
if LOGGING_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    LOGGING_LEVEL = "INFO"
logging.basicConfig(level=getattr(logging, LOGGING_LEVEL))
logger = logging.getLogger(__name__)

class InvalidDatabaseNameError(Exception):
    def __init__(self, message="Invalid database name."):
        self.message = message
        super().__init__(self.message)

class InvalidQuerySyntaxError(Exception):
    def __init__(self, message="Invalid SQL query syntax."):
        self.message = message
        super().__init__(self.message)

def validate_input(user_input, input_type):
    if input_type == "database":
        if not user_input:
            raise InvalidDatabaseNameError()
    elif input_type == "query":
        try:
            parse(user_input)
        except Exception as e:
            logger.error(f"Invalid SQL query syntax: {e}")
            raise InvalidQuerySyntaxError()

def should_continue():
    while True:
        choice = input("Do you want to continue? (y/n): ").strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            logger.warning("Invalid input. Please enter 'y' for yes or 'n' for no.")

while should_continue():
    database = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
    query = input("Enter SQL query (leave blank to use default): ") or "SELECT 1;"

    try:
        validate_input(database, "database")
        validate_input(query, "query")
    except InvalidDatabaseNameError as e:
        logger.error(e.message)
        continue
    except InvalidQuerySyntaxError as e:
        logger.error(e.message)
        continue

    try:
        conn = connect(database)
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        logger.info(f"Query executed successfully with {len(results)} rows returned.")
        conn.close()
    except Error as e:
        logger.error(f"Database error: {e}")
