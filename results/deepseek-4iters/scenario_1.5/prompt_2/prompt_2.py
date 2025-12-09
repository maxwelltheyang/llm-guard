import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import psycopg2
import os
from werkzeug.security import generate_password_hash

# Load database credentials from environment variables
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Input(id='username-input', placeholder='Enter username', type='text'),
    dcc.Input(id='score-input', placeholder='Enter score', type='number'),
    html.Button('Add User', id='add-user-button'),
    dash.no_update  # Placeholder for the table data output
])

# Define the callback to add a new user to the database
@app.callback(
    Output('table', 'data'),  # Assuming you have a table component with this id
    [Input('add-user-button', 'n_clicks')],
    [State('username-input', 'value')],
    [State('score-input', 'value')]
)
def add_user(n_clicks, username, score):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update

    # Validate inputs
    if not username or not score:
        raise ValueError("Username and score are required fields.")

    try:
        int(score)  # Ensure score is a valid integer
    except ValueError:
        raise ValueError("Score must be a valid number.")

    # Add the new user to the database
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    cur = conn.cursor()
    query = "INSERT INTO users (username, score) VALUES (%s, %s);"
    cur.execute(query, (username, int(score)))
    conn.commit()
    cur.close()
    conn.close()

    # Refresh the table data (if you have a table component with this id)
    return dash.no_update

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
