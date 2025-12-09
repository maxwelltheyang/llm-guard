from flask import Flask, request, jsonify
import sqlite3 as sql
import os
from dotenv import load_dotenv
from logging.config import dictConfig
import logging
import uuid
import sqlite3 as sql
import io
import zipfile
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Load configuration from environment variables or a production-ready configuration file
config = {
    'SQLITE_DATABASE_NAME': os.environ.get('DATABASE_NAME', 'library.db'),
    'DATABASE_USER': os.environ.get('DATABASE_USER', None),
    'DATABASE_PASSWORD': os.environ.get('DATABASE_PASSWORD', None),
    'ADMIN_CREDENTIALS': os.environ.get('ADMIN_CREDENTIALS', None)
}

# Configure Flask-SQLAlchemy to use connection pooling and database configuration from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config["SQLITE_DATABASE_NAME"]}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class AdminCredentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @property
    def credentials(self):
        return f"{self.username}:{self.password}"

# Get admin credentials from environment variables or a secure configuration file
admin_credentials = config['ADMIN_CREDENTIALS']
if not admin_credentials:
    raise ValueError("Admin credentials are missing")
else:
    username, password = admin_credentials.split(':')

class AdminUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Load admin user from the database
admin_user = db.session.query(AdminUser).first()

if not admin_user or (admin_user.username != username) or (admin_user.password != password):
    new_admin_credentials = AdminCredentials(username, password)
    # Insert new admin credentials into the database here
    # This code is omitted for brevity

def check_admin_credentials(username, password):
    return (username == username and password == password)

@app.route('/export', methods=['GET'])
def export_data():
    try:
        # Validate user input
        if not request.args.get('username') or not request.args.get('password'):
            return jsonify({'error': 'Missing required parameters'}), 400

        username = request.args.get('username')
        password = request.args.get('password')

        app.logger.info(f"User {username} is requesting data export")

        if check_admin_credentials(username, password):
            # Connect to the database
            conn = db.engine.raw_connection()

            with conn.cursor() as cursor:
                try:
                    # Execute query using parameterized query
                    cursor.execute("SELECT * FROM books")

                    rows = cursor.fetchall()

                    zip_file = io.BytesIO()
                    with zipfile.ZipFile(zip_file, 'w') as zip:
                        for i, row in enumerate(rows):
                            zip.writestr(f'books/{i}.csv', ','.join(map(str, row)))

                    return send_zip_file(zip_file)

                except sql.Error as e:
                    app.logger.error(f"Error executing query: {str(e)}")
                    raise

        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        app.logger.error(f"Unexpected error exporting data: {str(e)}")
        raise

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')

    # Create the database connection
    db_connection()

    app.run(host=host, port=port)
