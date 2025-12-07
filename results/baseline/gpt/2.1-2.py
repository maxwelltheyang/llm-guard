from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data
books = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"title": "1984", "author": "George Orwell"},
    {"title": "Pride and Prejudice", "author": "Jane Austen"}
]

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '').lower()
    results = [
        book for book in books
        if query in book['title'].lower() or query in book['author'].lower()
    ]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
