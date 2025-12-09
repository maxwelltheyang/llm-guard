import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging with INFO level to avoid excessive verbosity in a production environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure that all necessary environment variables are set
missing_env_vars = []
required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
for var in required_env_vars:
    if os.getenv(var) is None:
        missing_env_vars.append(var)
        logger.warning(f"Missing environment variable: {var}")
if missing_env_vars:
    error_message = f"The following environment variables are required but not set: {', '.join(missing_env_vars)}"
    logger.error(error_message)
    raise EnvironmentError(error_message)

# Callback function for login
@app.callback(
    Output('login-status', 'children'),
    [Input('username', 'value'), Input('password', 'value')]
)
def login(username, password):
    if not username or not password:
        logger.warning("Username or password missing for login")
        return "Please provide both username and password"

    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=generate_password_hash(password),  # Ensure hashed passwords
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        return f"Login failed due to database connection issue: {e}"

    # Additional security enhancements can be added here, such as parameterized queries and secure headers

    return "Login successful!"
