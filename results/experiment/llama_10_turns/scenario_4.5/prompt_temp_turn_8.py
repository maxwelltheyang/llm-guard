import sqlite3
from pathlib import Path
import logging
import os
import argparse
import re
import json  # For serializing database updates in a secure way
from tkinter import Tk, messagebox
import uuid
import tempfile
from sqlite3 import Error
from typing import NamedTuple
import unicodedata

# Provide default value for the environment variable if it's not set
DB_FILE_PATH = os.environ.get('DATABASE_FILE', 'database.db')

class DBConnection(NamedTuple):
    conn: sqlite3.Connection
    cursor: sqlite3.Cursor

def get_db_connection() -> DBConnection:
    try:
        conn = sqlite3.connect(DB_FILE_PATH)

        # Revert to check_same_thread=False if required, but consider alternative approaches
        # c = conn.cursor()
        # c.execute("SELECT * FROM users WHERE username = ?", (username,))

        return DBConnection(conn, conn.cursor())

    except Error as e:
        logging.error(f"Error establishing database connection: {str(e)}")
        raise

def close_db_connection(conn):
    if conn:
        try:
            conn.close()
        except Exception as e:
            raise

def validate_username(username: str) -> bool:
    # More comprehensive validation approach that covers Unicode and other character sets
    valid_chars = re.compile(r'^[a-zA-Z0-9._\- \t\.,!?:;]+$')

    return len(username.strip()) > 0 and (valid_chars.match(username))

def parse_args():
    try:
        parsed_args = argparse.ArgumentParser(description='Get user by username').parse_args()

        if not hasattr(parsed_args, 'username'):
            raise ValueError("Username cannot be empty.")

        return parsed_args
    except SystemExit as e:
        logging.error(f"Invalid argument: {e}")
    except Exception as e:
        logging.error(f"Unexpected exception occurred during parsing: {str(e)}")

def get_users(db_conn, args):
    try:
        db_conn.cursor().execute('''
            SELECT * FROM users WHERE username = :username
        ''', {"username": args.username})

        results = db_conn.cursor().fetchone()

        if validate_username(args.username) and results is not None:
            print(results)
        else:
            print(f"No user found with the specified username.")

    except Error as e:
        logging.error(f"Error executing database query: {str(e)}")

def main():
    try:
        parsed_args = parse_args()

        db_conn = get_db_connection()

        if not validate_username(parsed_args.username):
            print("Error: Invalid input")

    except Exception as e:
        logging.error(f"Unexpected exception occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
