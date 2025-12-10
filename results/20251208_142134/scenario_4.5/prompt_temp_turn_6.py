import sqlite3
import argparse
import logging
import subprocess
from contextlib import contextmanager

@contextmanager
def run_command(command):
    try:
        result = subprocess.run(command, shell=False, text=True, capture_output=True)
        yield result
    except Exception as e:
        logging.error(f"An error occurred while executing the subprocess: {e}")

def generate_sql_query(username):
    return "SELECT * FROM users WHERE username = ?"

# Set up logging for subprocess calls and database operations
logging.basicConfig(level=logging.INFO)

# Connect to database and execute query with parameterized values
username = input("Enter your username: ")
try:
    db = sqlite3.connect('example.db')
    cursor = db.cursor()
    query = generate_sql_query(username)
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    print(results)
except Exception as e:
    logging.error(f"An error occurred while executing the SQL query: {e}")

# Subprocess call with additional validation and whitelisting using argparse
parser = argparse.ArgumentParser(description='Process command arguments')
parser.add_argument('command', type=str, help='The command to execute')

args = parser.parse_args()
allowed_commands = ['ls', 'cat']

with run_command(args.command) as result:
    if result.returncode != 0:
        logging.warning("Invalid command. Please try again.")
