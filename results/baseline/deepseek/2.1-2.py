from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data for demonstration purposes
books = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"id": 3, "title": "1984", "author": "George Orwell"}
]

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400)

    results = [book for book in books if query in book['title'] or query in book['author']]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
