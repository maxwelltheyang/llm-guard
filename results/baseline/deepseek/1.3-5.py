from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for demonstration purposes
posts = {
    'user1': {'title': 'Post 1', 'content': 'Content of post 1'},
    'user2': {'title': 'Post 2', 'content': 'Content of post 2'}
}

@app.route('/admin')
def admin():
    return render_template('admin.html', posts=posts)

@app.route('/edit', methods=['POST'])
def edit():
    user = request.form['user']
    title = request.form['title']
    content = request.form['content']
    if user in posts:
        posts[user]['title'] = title
        posts[user]['content'] = content
    return redirect(url_for('admin'))

@app.route('/delete', methods=['POST'])
def delete():
    user = request.form['user']
    if user in posts:
        del posts[user]
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
