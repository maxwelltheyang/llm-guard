from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for demonstration purposes
books = []

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.get_json()
    if 'title' in new_book and 'author' in new_book:
        books.append(new_book)
        return jsonify({'message': 'Book added successfully'}), 201
    else:
        return jsonify({'error': 'Invalid book data'}), 400

if __name__ == '__main__':
    app.run(debug=True)
