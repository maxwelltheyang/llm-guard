from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['library']
books_collection = db['books']

@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    books = []
    for book in books_collection.find():
        if query.lower() in book['title'].lower() or query.lower() in book['author'].lower():
            books.append({
                '_id': str(book['_id']),
                'title': book['title'],
                'author': book['author']
            })

    return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True)
