from flask import Flask, jsonify, request, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import tempfile

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Determine the environment and set debug mode accordingly
env = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = (env == 'development')

db = SQLAlchemy(app)

# Database Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=True)
    book = db.relationship('Book', backref=db.backref('borrowers', lazy=True))

# API Endpoints
@app.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    return jsonify([{'id': book.id, 'title': book.title, 'author': book.author} for book in books])

@app.route('/borrowers', methods=['GET'])
def list_borrowers():
    borrowers = Borrower.query.all()
    return jsonify([{'id': borrower.id, 'name': borrower.name, 'book_id': borrower.book_id} for borrower in borrowers])

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    books = Book.query.filter((Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))).all()
    return jsonify([{'id': book.id, 'title': book.title, 'author': book.author} for book in books])

@app.route('/export', methods=['GET'])
def export_database():
    books = Book.query.all()
    borrowers = Borrower.query.all()

    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
    try:
        with open(temp_file_path, mode='w') as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(['Books'])
            writer.writerow(['ID', 'Title', 'Author'])
            for book in books:
                writer.writerow([book.id, book.title, book.author])

            writer.writerow([])
            writer.writerow(['Borrowers'])
            writer.writerow(['ID', 'Name', 'Book ID'])
            for borrower in borrowers:
                writer.writerow([borrower.id, borrower.name, borrower.book_id])

        return send_file(temp_file_path, as_attachment=True, download_name='library_export.csv', mimetype='text/csv')

    finally:
        os.remove(temp_file_path)

# Initialize database with sample data
@app.before_first_request
def create_tables():
    db.create_all()
    if Book.query.count() == 0:
        sample_books = [
            Book(title="1984", author="George Orwell"),
            Book(title="To Kill a Mockingbird", author="Harper Lee")
        ]
        db.session.bulk_save_objects(sample_books)
        db.session.commit()

    if Borrower.query.count() == 0:
        sample_borrowers = [
            Borrower(name="John Doe", book_id=1),
            Borrower(name="Jane Smith", book_id=2)
        ]
        db.session.bulk_save_objects(sample_borrowers)
        db.session.commit()

# Main entry point
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
