# Assuming you are using Flask for the web framework and SQLAlchemy for database operations
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Fetch all posts from the database
    posts = fetch_posts()  # Implement this function to fetch posts from your database
    return render_template('index.html', posts=posts)

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    posts = search_posts(keyword)  # Implement this function to search posts by keyword in your database
    return render_template('index.html', posts=posts, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)
