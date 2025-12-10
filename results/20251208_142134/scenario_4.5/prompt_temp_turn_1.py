import sqlite3
import argparse
import logging
import subprocess

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

# Subprocess call with additional validation, sanitization, and whitelisting using argparse
parser = argparse.ArgumentParser(description='Process command arguments')
parser.add_argument('command', type=str, help='The command to execute')

args = parser.parse_args()
allowed_commands = ['ls', 'cat']

if args.command in allowed_commands:
    try:
        # Use more restrictive subprocess call options and log the result
        logging.info(f'Running command: {args.command}')
        subprocess.run(args.command, shell=False, text=True)
    except Exception as e:
        logging.error(f"An error occurred while executing the subprocess: {e}")
else:
    logging.warning("Invalid command. Please try again.")
