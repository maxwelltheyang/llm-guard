from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Database to store posts (in memory for simplicity)
posts = {}

@app.route('/')
def index():
    return render_template('index.html', posts=list(posts.values()))

@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        id = str(len(posts) + 1)
        posts[id] = {'title': title, 'content': content}
        return render_template('new-post.html', success=True)
    else:
        return render_template('new-post.html')

@app.route('/post/<id>')
def view_post(id):
    if id in posts:
        post = posts[id]
        return render_template('view-post.html', post=post)
    else:
        return 'Post not found'

if __name__ == '__main__':
    app.run(debug=True)

# HTML templates
app.template_folder = os.path.join(os.getcwd(), 'templates')

@app.context_processor
def inject():
    def get_posts():
        return posts.values()
    return {'get_posts': get_posts}
