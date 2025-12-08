from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory storage for reviews
reviews = []

@app.route('/')
def index():
    return render_template('index.html', reviews=reviews)

@app.route('/add_review', methods=['POST'])
def add_review():
    user_name = request.form.get('user_name')
    product_id = request.form.get('product_id')
    rating = request.form.get('rating')
    comment = request.form.get('comment')

    review = {
        'user_name': user_name,
        'product_id': product_id,
        'rating': rating,
        'comment': comment
    }

    reviews.append(review)
    return jsonify({'status': 'success', 'message': 'Review added successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
