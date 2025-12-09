import mysql.connector
from mysql.connector import errorcode
import hashlib
import secrets
import re
import os
import sqlite3

# Database connection setup
def get_db_connection():
    try:
        conn = mysql.connector.connect(user='root', password='password', host='localhost', database='mydatabase')
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

# Register User Function
def registerUser(username, password):
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        # Using parameterized query to prevent SQL injection
        add_user_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(add_user_query, (username, hashed_password))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print("Database error:", err)
        return False
    finally:
        cursor.close()
        conn.close()

# CSRF Token Generation and Verification
def generate_csrf_token():
    return secrets.token_hex(16)

def verify_csrf_token(request, token):
    if 'csrf_token' not in request.session or request.session['csrf_token'] != token:
        raise ValueError("CSRF token verification failed")

# Example of a form with CSRF protection
def show_form():
    csrf_token = generate_csrf_token()
    # Store the generated token in session for later validation
    request.session['csrf_token'] = csrf_token
    return f'''<form method="post" action="/submit-form">
                    <input type="hidden" name="csrf_token" value="{csrf_token}">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username"><br><br>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password"><br><br>
                    <input type="submit" value="Submit">
                </form>'''

# Improved Error Handling in Login Function
def login(username, password):
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        # Using parameterized query for better security
        login_query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cursor.execute(login_query, (username, hashed_password))
        user = cursor.fetchone()
        if user:
            return True
        else:
            return False
    except mysql.connector.Error as err:
        print("Database error:", err)
        return False
    finally:
        cursor.close()
        conn.close()

# Main application logic would go here, including routes for handling forms and submissions
