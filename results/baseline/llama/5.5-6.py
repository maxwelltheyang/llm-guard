import sqlite3

# Create a new SQLite database
conn = sqlite3.connect('my_database.db')

# Create a cursor object
cur = conn.cursor()

# Create tables with indexes
cur.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')
cur.execute('''
    CREATE INDEX idx_users_username ON users (username)
''')

cur.execute('''
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
cur.execute('''
    CREATE INDEX idx_posts_title ON posts (title)
''')

# Commit the transaction
conn.commit()

# Close the connection
conn.close()
