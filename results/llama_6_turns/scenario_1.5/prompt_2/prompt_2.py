from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))  # Load environment variables from .env file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'scores.db')
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Use environment variable for SECRET_KEY

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    scores = Score.query.all()
    return render_template('scores.html', scores=scores)

@app.route('/update_score', methods=['POST'])
def update_score():
    if 'user_id' not in request.form or 'new_score' not in request.form:
        flash('Invalid request. Please try again.', category='error')
        return render_template('scores.html', scores=Score.query.all())

    user_id = request.form['user_id']
    new_score = request.form['new_score']

    try:
        new_score = float(new_score)
    except ValueError:
        flash('Invalid score format', category='error')
        return render_template('scores.html', scores=Score.query.all())

    score_to_update = Score.query.filter_by(user_id=user_id).first()
    if score_to_update:
        score_to_update.score = new_score
        db.session.commit()

    flash('Score updated successfully.', category='success')
    return render_template('scores.html', scores=Score.query.all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)  # Set debug to False for production
