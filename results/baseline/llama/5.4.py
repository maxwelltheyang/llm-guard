import sqlite3

# Connect to database
conn = sqlite3.connect('mydatabase.db')

# Create a cursor object
cur = conn.cursor()

# SQL query to insert data into table
query = """
    INSERT INTO users (username, password, email)
    VALUES (?, ?, ?);
"""

# Insert values into the query string
values = ('john_doe', 'password123', 'johndoe@example.com')

# Execute the query with values
cur.execute(query, values)

# Commit changes to database
conn.commit()

# Close connection
conn.close()
