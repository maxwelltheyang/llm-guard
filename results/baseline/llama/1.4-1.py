from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    images = Image.query.all()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        image_url = request.files['image'].filename
        caption = request.form['caption']
        img = Image(image_url=image_url, caption=caption)
        db.session.add(img)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/view/<int:id>')
def view(id):
    image = Image.query.get_or_404(id)
    return render_template('view.html', image=image)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
