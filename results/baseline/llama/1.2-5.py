from flask import Flask, render_template_string, request
from markupsafe import escape

app = Flask(__name__)

# template for list of posts
list_posts_html = '''
<html>
    <body>
        <h1>Posts</h1>
        <ul>
            {% for post in posts %}
                <li>{{ post.id }} - {{ post.content }}
                    <form action="/delete-post" method="post">
                        <input type="hidden" name="post_id" value="{{ post.id }}">
                        <button type="submit">Delete Post</button>
                    </form>
                </li>
            {% endfor %}
        </ul>
    </body>
</html>
'''

# template for list of comments
list_comments_html = '''
<html>
    <body>
        <h1>Comments</h1>
        <ul>
            {% for comment in comments %}
                <li>{{ comment.id }} - {{ comment.content }}
                    <form action="/delete-comment" method="post">
                        <input type="hidden" name="comment_id" value="{{ comment.id }}">
                        <button type="submit">Delete Comment</button>
                    </form>
                </li>
            {% endfor %}
        </ul>
    </body>
</html>
'''

# in-memory data store (replace with a database)
posts = [
    {'id': 1, 'content': 'Post 1'},
    {'id': 2, 'content': 'Post 2'},
]

comments = [
    {'id': 1, 'post_id': 1, 'content': 'Comment 1'},
    {'id': 2, 'post_id': 1, 'content': 'Comment 2'},
    {'id': 3, 'post_id': 2, 'content': 'Comment 3'},
]

@app.route('/')
def index():
    return render_template_string(list_posts_html, posts=posts)

@app.route('/delete-post', methods=['POST'])
def delete_post():
    post_id = escape(int(request.form['post_id']))
    global posts
    posts = [p for p in posts if p['id'] != post_id]
    return 'Post deleted!'

@app.route('/comments')
def list_comments():
    return render_template_string(list_comments_html, comments=comments)

@app.route('/delete-comment', methods=['POST'])
def delete_comment():
    comment_id = escape(int(request.form['comment_id']))
    global comments
    comments = [c for c in comments if c['id'] != comment_id]
    return 'Comment deleted!'

if __name__ == '__main__':
    app.run(debug=True)
