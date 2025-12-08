from flask import Flask, request, render_template

app = Flask(__name__)

# Sample data store for reviews
reviews = []

@app.route('/')
def index():
    return render_template('index.html', reviews=reviews)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    name = request.form['name']
    comment = request.form['comment']
    review = {'name': name, 'comment': comment}
    reviews.append(review)
    return render_template('index.html', reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True)
