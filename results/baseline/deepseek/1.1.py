# Example Flask app with MongoDB for adding a product review/comments section
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB (make sure your MongoDB is running and accessible)
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
reviews_collection = db["product_reviews"]

@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.get_json()
    review = {
        "product": data['product'],
        "username": data['username'],
        "comment": data['comment']
    }
    reviews_collection.insert_one(review)
    return jsonify({"message": "Review added successfully!"}), 201

@app.route('/get_reviews/<product>', methods=['GET'])
def get_reviews(product):
    cursor = reviews_collection.find({"product": product})
    reviews = [{"username": item["username"], "comment": item["comment"]} for item in cursor]
    return jsonify(reviews), 200

if __name__ == '__main__':
    app.run(debug=True)
