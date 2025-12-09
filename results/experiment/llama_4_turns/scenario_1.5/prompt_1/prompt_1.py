from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)
# Disable debug mode in production environments
if app.config.get('DEBUG'):
    print("Debug mode is enabled")
else:
    print("Production environment detected")

if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite') and not app.config.get('DEBUG', False):
    logging.error("Database URI does not match production environment. Exiting.")
    exit()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'  # Replace with your database URI
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
    app.run(debug=app.config.get('DEBUG', False))
