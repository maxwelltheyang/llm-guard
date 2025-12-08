from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        results = Post.query.filter(
            (Post.title.contains(keyword)) | (Post.content.contains(keyword))
        ).all()
        return render_template('index.html', posts=results)

    posts = Post.query.all()
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
