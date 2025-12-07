from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(200), nullable=True)
    is_flagged = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    images = Image.query.all()
    return render_template('index.html', images=images)

@app.route('/admin')
def admin():
    flagged_images = Image.query.filter_by(is_flagged=True).all()
    return render_template('admin.html', images=flagged_images)

@app.route('/flag/<int:image_id>', methods=['POST'])
def flag(image_id):
    image = Image.query.get_or_404(image_id)
    image.is_flagged = True
    db.session.commit()
    flash('Image has been flagged for review.')
    return redirect(url_for('index'))

@app.route('/remove/<int:image_id>', methods=['POST'])
def remove(image_id):
    image = Image.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Image has been removed.')
    return redirect(url_for('admin'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
