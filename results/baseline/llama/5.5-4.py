import sqlite3

# Connect to database
conn = sqlite3.connect('database.db')

# Create a cursor object
c = conn.cursor()

# Grant SELECT, INSERT, UPDATE, DELETE privileges without admin rights
c.execute("""
    GRANT SELECT, INSERT, UPDATE, DELETE
    ON TABLE_NAME TO 'username'@'hostname';
""")

# Commit changes
conn.commit()

# Close connection
conn.close()
