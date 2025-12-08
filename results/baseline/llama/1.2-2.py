from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
db = SQLAlchemy(app)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    comments = db.relationship('Comment', backref='blog_post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    if request.method == 'POST':
        comment = Comment(text=request.form['comment'], blog_post_id=post_id)
        db.session.add(comment)
        db.session.commit()

    return render_template('post.html', post=post, comments=post.comments)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
