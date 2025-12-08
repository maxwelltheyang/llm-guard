from flask import Flask, request, send_from_directory, jsonify, session
import os
import stat
import grp
import pwd
import argparse
import sys
import sqlite3
import logging
import argon2
import secrets
from threading import Lock

app = Flask(__name__)
# Secret key for Flask sessions
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

class User:
    def __init__(self):
        self.password_hasher = argon2.PasswordHasher()
        self.lock = Lock()

    @staticmethod
    def verify_password(password, stored_hash):
        try:
            return User().password_hasher.verify(password, stored_hash)
        except Exception as e:
            logging.error(e)

class Database:
    db_name = 'secure_code.db'
    conn = None
    cursor = None

    @classmethod
    def get_db_connection(cls):
        if cls.conn is None or not cls.conn.is_connected():
            cls.conn = sqlite3.connect(Database.db_name)
            cls.cursor = cls.conn.cursor()
        return cls.conn

def create_tables():
    try:
        Database.get_db_connection().executescript("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash BLOB,
                salt BLOB,
                iteration_count INTEGER
            )
        """)
    except sqlite3.Error as e:
        logging.error(e)
    finally:
        if Database.conn is not None and Database.conn.is_connected():
            Database.conn.close()

def register_user(username, password):
    user_instance.lock.acquire()
    try:
        hashed_password = user_instance.password_hasher.hash(password)
        salt = user_instance.password_hasher.salt
        iteration_count = user_instance.password_hasher.params['t']
        Database.get_db_connection().execute("INSERT INTO users (username, password_hash, salt, iteration_count) VALUES (?, ?, ?, ?)",
                                              (username, hashed_password, salt, iteration_count))
        Database.conn.commit()
    except sqlite3.Error as e:
        logging.error(e)
    finally:
        user_instance.lock.release()

def login_user(username, password):
    user_instance.lock.acquire()
    try:
        Database.get_db_connection().execute("SELECT * FROM users WHERE username=?", (username,))
        user_data = Database.cursor.fetchone()
        if user_data and User.verify_password(password, user_data[1]):
            session['logged_in'] = True
            return 'Logged in successfully!'
        else:
            return 'Invalid username or password'
    except sqlite3.Error as e:
        logging.error(e)
    finally:
        user_instance.lock.release()

def generate_password_hash(password):
    try:
        global user_instance
        if not user_instance:
            user_instance = User()
        # Generate the hash with Argon2
        hashed_password = user_instance.password_hasher.hash(password)
        return hashed_password
    except Exception as e:
        logging.error(e)
        sys.exit(1)

if __name__ == '__main__':
    create_tables()  # Create tables at application startup
    app.run(host='127.0.0.1', port=5000)
