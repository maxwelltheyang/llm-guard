from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    if 'title' in data and 'author' in data:
        book = Book(title=data['title'], author=data['author'])
        db.session.add(book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 200
    else:
        return jsonify({'error': 'Missing required fields'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
