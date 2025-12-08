import sqlite3

def query_db(query, params=()):
    conn = sqlite3.connect('example.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

# Example usage:
result = query_db('SELECT * FROM users WHERE age > ?', (25,))
for row in result:
    print(row['name'])
