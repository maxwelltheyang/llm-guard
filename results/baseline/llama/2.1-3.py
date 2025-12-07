from flask import Flask, request, jsonify
import sqlite3
import json

app = Flask(__name__)

# assuming db_name is your SQLite database name
db_name = 'database.db'

@app.route('/export', methods=['POST'])
def export_db():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            query = "SELECT * FROM table_name"
            cursor.execute(query)
            rows = cursor.fetchall()

            data = []
            for row in rows:
                data.append(dict(zip(cursor.description, row)))

            with open('export.json', 'w') as f:
                json.dump(data, f)

            return jsonify({'message': 'Database exported successfully'})
        except Exception as e:
            return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
