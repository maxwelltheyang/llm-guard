import sqlite3
from urllib.parse import urlparse, parse_qs

def get_data(url):
    try:
        parsed_url = urlparse(url)
        db_name = parsed_url.path.strip('/')

        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM table"
            cursor.execute(query)

            data = cursor.fetchall()

            return {"data": data}
    except sqlite3.Error as e:
        # Don't expose the actual error message
        return {"error": "Database error"}
