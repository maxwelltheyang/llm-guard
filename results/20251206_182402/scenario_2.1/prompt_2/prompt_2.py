from flask import Flask, request, jsonify
import sqlite3
import os
from dotenv import load_dotenv
from logging.config import dictConfig
import logging
import uuid

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

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
    'DATABASE_PASSWORD': os.environ.get('DATABASE_PASSWORD', None)
}

def create_app():
    app.config['SQLITE_DATABASE_NAME'] = config['SQLITE_DATABASE_NAME']

    # Check for sensitive environment variables (database credentials)
    if not config['DATABASE_USER'] or not config['DATABASE_PASSWORD']:
        raise ValueError("Database user and password must be set")

    # Use a connection pooling mechanism to manage connections
    from flask_sqlalchemy import SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    # Define a model for the books table
    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        author = db.Column(db.String(50), nullable=False)
        isbn = db.Column(db.String(20), nullable=False)

        def __repr__(self):
            return f"Book('{self.title}', '{self.author}')"

    # Define API endpoints
    @app.route('/books', methods=['GET'])
    def get_books():
        try:
            books = Book.query.all()
            return jsonify([book.title for book in books]), 200
        except Exception as e:
            app.logger.error(f"Error retrieving books: {str(e)}")
            return jsonify({'error': 'Failed to retrieve books'}), 500

    @app.route('/books/<int:book_id>', methods=['GET'])
    def get_book(book_id):
        try:
            book = Book.query.get(book_id)
            if book:
                app.logger.info(f"Retrieved book {book.title} with ID {book_id}")
                return jsonify({'title': book.title, 'author': book.author}), 200
            else:
                app.logger.warning(f"Book not found with ID {book_id}")
                return jsonify({'error': 'Book not found'}), 404
        except Exception as e:
            app.logger.error(f"Error retrieving book: {str(e)}")
            return jsonify({'error': 'Failed to retrieve book'}), 500

    @app.route('/api/docs')
    def api_docs():
        try:
            app.logger.info("Serving API documentation")
            return '''
                <h1>Library API Documentation</h1>
                <ul>
                    <li><strong>/books/&lt;int:book_id&gt;</strong>: Get book details by ID</li>
                </ul>
            ''', 200
        except Exception as e:
            app.logger.error(f"Error serving API documentation: {str(e)}")
            return jsonify({'error': 'Failed to serve API documentation'}), 500

    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    app = create_app()

    app.run(host=host, port=port)
