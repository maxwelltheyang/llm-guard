from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    posts = Post.query.all()

    if request.method == 'POST':
        if 'edit' in request.form:
            post_id = request.form.get('edit')
            return redirect(url_for('edit_post', post_id=post_id))

        elif 'delete' in request.form:
            post_id = request.form.get('delete')
            post = Post.query.get_or_404(post_id)
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('admin'))

    return render_template('admin.html', posts=posts)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post.title = title
        post.content = content
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('edit_post.html', post=post)

if __name__ == "__main__":
    app.run(debug=True)
