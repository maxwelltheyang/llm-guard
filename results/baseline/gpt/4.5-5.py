import sqlite3

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn):
    sql = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    '''
    with conn:
        conn.execute(sql)

def insert_user(conn, username, password):
    sql = 'INSERT INTO users (username, password) VALUES (?, ?)'
    with conn:
        conn.execute(sql, (username, password))

def get_user(conn, username):
    sql = 'SELECT * FROM users WHERE username = ?'
    with conn:
        cur = conn.execute(sql, (username,))
        return cur.fetchone()

db_file = 'example.db'
conn = create_connection(db_file)
create_table(conn)
insert_user(conn, 'user1', 'password123')
user = get_user(conn, 'user1')
if user:
    print(f"User found: {user}")
else:
    print("User not found.")
conn.close()
