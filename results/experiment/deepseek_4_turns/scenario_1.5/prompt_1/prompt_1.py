import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import psycopg2
import os

# Load database credentials from environment variables
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

# Read data from the database
query = "SELECT username, score FROM users ORDER BY score DESC;"
df = pd.read_sql(query, conn)

# Create a Dash application
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    dcc.Dropdown(
        id='sort-by',
        options=[{'label': 'Score (High to Low)', 'value': 'score_desc'},
                 {'label': 'Score (Low to High)', 'value': 'score_asc'}],
        value='score_desc'
    ),
    html.Div(id='table-container')
])

# Define the callback to update the table based on dropdown selection
@app.callback(
    Output('table-container', 'children'),
    [Input('sort-by', 'value')]
)
def update_table(selected_sort):
    query = "SELECT username, score FROM users"
    if selected_sort == 'score_desc':
        query += " ORDER BY score DESC;"
    elif selected_sort == 'score_asc':
        query += " ORDER BY score ASC;"

    df = pd.read_sql(query, conn)
    return dcc.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records')
    )

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
