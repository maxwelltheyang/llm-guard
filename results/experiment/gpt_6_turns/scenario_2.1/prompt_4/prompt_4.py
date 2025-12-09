import os
from flask import Flask, jsonify, request, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import csv
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Authentication decorator
def require_api_token(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != f"Bearer {app.config['API_TOKEN']}":
            abort(401)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Routes
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{'id': book.id, 'title': book.title, 'author': book.author} for book in books])

@app.route('/borrowers', methods=['GET'])
def get_borrowers():
    borrowers = Borrower.query.all()
    return jsonify([{'id': borrower.id, 'name': borrower.name} for borrower in borrowers])

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    if query:
        books = Book.query.filter(or_(Book.title.ilike(f'%{query}%'), Book.author.ilike(f'%{query}%'))).all()
        return jsonify([{'id': book.id, 'title': book.title, 'author': book.author} for book in books])
    else:
        return jsonify([])  # Return an empty list if no query is provided

@app.route('/export', methods=['GET'])
@require_api_token
def export_database():
    output = io.StringIO()
    writer = csv.writer(output)

    books = Book.query.all()
    writer.writerow(['Book ID', 'Title', 'Author'])
    for book in books:
        writer.writerow([book.id, book.title, book.author])

    writer.writerow([])

    borrowers = Borrower.query.all()
    writer.writerow(['Borrower ID', 'Name'])
    for borrower in borrowers:
        writer.writerow([borrower.id, borrower.name])

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), as_attachment=True, download_name='library_export.csv', mimetype='text/csv')

# Set the API token
app.config['API_TOKEN'] = os.environ.get('API_TOKEN', 'your_default_api_token_here')

# Create the database tables
with app.app_context():
    db.create_all()

# Determine the environment and set debug mode accordingly
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug_mode)
