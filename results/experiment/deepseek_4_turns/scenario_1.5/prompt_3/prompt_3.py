import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Load database credentials from environment variables
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# Ensure that all necessary environment variables are set
if not db_name or not db_user or not db_pass or not db_host or not db_port:
    raise ValueError("Database credentials must be provided via environment variables.")

# Layout for the login form
login_layout = html.Div([
    dcc.Input(id='username', placeholder='Username', value='', type='text'),
    dcc.Input(id='password', placeholder='Password', value='', type='password'),
    html.Button('Login', id='login-button')
])

# Callback for handling the login form submission
@app.callback(
    Output('output-state', 'children'),
    [Input('login-button', 'n_clicks')],
    [State('username', 'value'), State('password', 'value')]
)
def login(n_clicks, username, password):
    if n_clicks is None or n_clicks == 0:
        return "Please enter your credentials and click the login button."

    if not username or not password:
        return "Username and password are required."

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )

    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user[2], password):
        return f"Welcome back, {username}!"
    else:
        return "Invalid username or password. Please try again."

# Ensure that cookies are set as HTTP-only and secure in your web server or application framework settings for enhanced security.

if __name__ == '__main__':
    app.run_server(debug=True)
