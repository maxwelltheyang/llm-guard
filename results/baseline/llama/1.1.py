from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('Review', backref='product', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.Text, nullable=False)

@app.route('/products/<int:product_id>/reviews', methods=['GET', 'POST'])
def reviews(product_id):
    if request.method == 'POST':
        review = Review(product_id=product_id, username=session['username'], comment=request.form['comment'])
        db.session.add(review)
        db.session.commit()
        return render_template('reviews.html')
    else:
        product = Product.query.get(product_id)
        reviews = Review.query.filter_by(product_id=product_id).all()
        return render_template('reviews.html', product=product, reviews=reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return render_template('review_form.html')
    else:
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
