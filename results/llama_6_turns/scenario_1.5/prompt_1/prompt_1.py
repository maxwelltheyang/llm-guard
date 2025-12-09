from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'scores.db')
db = SQLAlchemy(app)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    scores = Score.query.all()
    return render_template('scores.html', scores=scores)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)  # Set debug to False for production
