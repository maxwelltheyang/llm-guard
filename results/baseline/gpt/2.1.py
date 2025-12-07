from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample in-memory book list
books = []

@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.json
    books.append(new_book)
    return jsonify(new_book), 201

if __name__ == '__main__':
    app.run(debug=True)
