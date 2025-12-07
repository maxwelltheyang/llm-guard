import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import logging
from wtforms import Form, StringField, FloatField, validators

app = Flask(__name__)

# Load environment variables for secure configuration
if 'DATABASE_URI' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
else:
    # Use a default or local database URI as fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'

# Disable debug mode by default to prevent exposure of sensitive data
app.config['DEBUG'] = False

db = SQLAlchemy(app)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Float, nullable=False)

class UpdateScoreForm(Form):
    user_id = StringField('User ID', [validators.DataRequired()])
    new_score = FloatField('New Score', [validators.NumberRange(min=0, max=100, message='Score must be between 0 and 100')])

@app.route('/')
def index():
    scores = Score.query.all()
    return render_template('scores.html', scores=scores)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/update_score', methods=['POST'])
@limiter.limit("10 per minute")
def update_score():
    form = UpdateScoreForm(request.form)

    if form.validate_on_submit():
        user_id = form.user_id.data
        new_score = float(form.new_score.data)

        score_to_update = Score.query.filter_by(user_id=user_id).first()
        if score_to_update:
            score_to_update.score = new_score
            db.session.commit()
            return 'Score updated successfully'
        else:
            new_score_entry = Score(user_id=user_id, score=new_score)
            db.session.add(new_score_entry)
            db.session.commit()
            return 'New score entry created'
    else:
        return render_template('scores.html', scores=Score.query.all(), form_errors=form.errors)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=app.config.get('DEBUG'))
