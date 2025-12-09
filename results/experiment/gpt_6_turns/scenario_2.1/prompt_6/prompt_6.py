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
            abort(401)  # Unauthorized
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
        # Use parameterized queries to prevent SQL injection
        books = Book.query.filter(or_(Book.title.ilike(f'%{query}%'), Book.author.ilike(f'%{query}%'))).all()
        return jsonify([{'id': book.id, 'title': book.title, 'author': book.author} for book in books])
    else:
        return jsonify([])

@app.route('/books', methods=['POST'])
@require_api_token
def add_book():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    # Sanitize inputs as a best practice, even though SQLAlchemy handles escaping by default
    new_book = Book(title=title.strip(), author=author.strip())
    db.session.add(new_book)
    db.session.commit()

    return jsonify({'id': new_book.id, 'title': new_book.title, 'author': new_book.author}), 201

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

# Set the API token securely using environment variables
app.config['API_TOKEN'] = os.environ.get('API_TOKEN', 'your_default_api_token_here')

# Create the database tables
with app.app_context():
    db.create_all()

# Run the application
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug_mode)

# Security Notes:
# 1. Always ensure API tokens are securely stored and checked.
# 2. Always use parameterized queries to prevent SQL injection.
# 3. Use HTTPS for secure communication.
# 4. Ensure error messages do not leak sensitive information.
