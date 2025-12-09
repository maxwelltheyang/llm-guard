from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

app = Flask(__name__)

# Load secret key from environment variable for improved security
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

posts = []

@app.route('/')
def index():
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title or not content:
            flash('Title and content are required!')
            return redirect(url_for('create'))

        new_post = {
            'title': title,
            'content': content,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'comments': []
        }
        posts.append(new_post)
        flash('Post created successfully!')
        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    if post_id < 0 or post_id >= len(posts):
        flash('Post not found!')
        return redirect(url_for('index'))
    post = posts[post_id]

    if request.method == 'POST':
        comment_content = request.form.get('comment')
        if comment_content:
            comment = {
                'content': comment_content,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            post['comments'].append(comment)
            flash('Comment added successfully!')
            return redirect(url_for('post', post_id=post_id))
        else:
            flash('Comment cannot be empty!')

    return render_template('post.html', post=post)

if __name__ == '__main__':
    # Ensure the debug mode is configurable via an environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode)
