from flask import Flask, render_template, request

app = Flask(__name__)

# Database schema for storing reviews
class Review:
    def __init__(self, id, user_name, rating, comment):
        self.id = id
        self.user_name = user_name
        self.rating = rating
        self.comment = comment

reviews = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post_review', methods=['POST'])
def post_review():
    review_id = len(reviews) + 1
    reviews.append(Review(review_id, request.form['user_name'], int(request.form['rating']), request.form['comment']))
    return 'Review posted successfully!'

@app.route('/view_reviews')
def view_reviews():
    return render_template('reviews.html', reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True)
