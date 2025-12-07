from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'example.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/export', methods=['GET'])
def export_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all rows from the database
    cursor.execute("SELECT * FROM your_table_name")  # Replace 'your_table_name' with the actual table name
    rows = cursor.fetchall()

    # Create a temporary file to store the data
    temp_file_path = '/tmp/exported_db.json'
    with open(temp_file_path, 'w') as f:
        for row in rows:
            f.write(str(row) + '\n')

    # Send the file to the user
    response = jsonify({"message": "Database exported successfully", "file_path": temp_file_path})
    os.remove(temp_file_path)  # Clean up temporary file

    return response

if __name__ == '__main__':
    app.run(debug=True)
