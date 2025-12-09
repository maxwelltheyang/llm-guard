import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Securely get the secret key from an environment variable
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret')  # Ensure 'default_secret' is appropriate for non-production environments only

# Configure the database connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# Create the database schema
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    # Fetch all user scores from the database
    users = User.query.all()
    return render_template('dashboard.html', users=users)

@app.route('/update/<int:user_id>', methods=['POST'])
def update_score(user_id):
    user = User.query.get(user_id)
    if user:
        new_score = request.form.get('new_score')
        # Validate the input
        if new_score and new_score.isdigit():
            new_score = int(new_score)
            if 0 <= new_score <= 100:  # Assuming score should be between 0 and 100
                user.score = new_score
                db.session.commit()
                flash("Score updated successfully!", "success")
            else:
                flash("Score must be between 0 and 100.", "error")
        else:
            flash("Invalid input. Please enter a valid number.", "error")
    else:
        flash("User not found.", "error")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Determine the environment and set the debug mode accordingly
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
