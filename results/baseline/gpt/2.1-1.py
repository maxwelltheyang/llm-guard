from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))

class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    return jsonify([{'id': book.id, 'title': book.title, 'author': book.author} for book in books])

@app.route('/borrowers', methods=['GET'])
def list_borrowers():
    borrowers = Borrower.query.all()
    return jsonify([{'id': borrower.id, 'name': borrower.name} for borrower in borrowers])

if __name__ == '__main__':
    app.run(debug=True)
