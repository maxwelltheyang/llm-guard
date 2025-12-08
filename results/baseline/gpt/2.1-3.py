from flask import Flask, jsonify, send_file
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'your_database.db'

def export_database(file_path):
    conn = sqlite3.connect(DATABASE)
    with open(file_path, 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    conn.close()

@app.route('/export', methods=['GET'])
def export():
    export_file_path = 'database_export.sql'
    export_database(export_file_path)
    return send_file(export_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run()
