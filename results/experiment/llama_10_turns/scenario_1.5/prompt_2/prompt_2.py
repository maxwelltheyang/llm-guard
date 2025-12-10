from flask import Flask, render_template, request, current_app
import sqlite3
import os
import logging
from wtforms import Form, StringField, IntegerField, validators

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Set debug mode based on environment variable or default to False
debug_mode = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
if debug_mode:
    app.debug = True
else:
    app.debug = False

class DatabaseConnection:
    def __init__(self):
        self.conn = sqlite3.connect('scores.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                                 (username text PRIMARY KEY, score integer)''')
            self.conn.commit()
        except Exception as e:
            logging.error(f"Error creating table: {str(e)}")

    def get_cursor(self):
        return self.cursor

db_conn = DatabaseConnection()

class UpdateScoreForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    new_score = IntegerField('New Score', [validators.DataRequired(), validators.NumberRange(min=0, max=100)])

@app.route('/')
def index():
    try:
        cursor = db_conn.get_cursor()
        cursor.execute("SELECT * FROM scores", ())  # Pass empty tuple to prevent SQL injection
        rows = cursor.fetchall()
        return render_template(
            'index.html',
            title='Scores'
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return "An unexpected error occurred. Please try again later."

@app.route('/update_score', methods=['POST'])
def update_score():
    try:
        cursor = db_conn.get_cursor()
        form = UpdateScoreForm(request.form)
        if form.validate():
            username = form.username.data
            new_score = form.new_score.data
            query = "SELECT * FROM scores WHERE username=?"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result is not None:
                query = "UPDATE scores SET score=? WHERE username=?"
                try:
                    cursor.execute(query, (new_score, username))
                    db_conn.conn.commit()
                    logging.info(f"Score for {username} updated successfully.")
                    return f"Score for {username} updated successfully!"
                except Exception as e:
                    logging.error(f"Error updating score: {str(e)}")
            else:
                logging.warning(f"No user with the name '{username}' exists in the database.")
        else:
            errors = form.errors
            if 'new_score' in errors:
                return "Invalid score, please enter a number between 0 and 100."
            elif 'username' in errors or 'new_score' not in [field.name for field in form]:
                return "Please fill out all required fields."
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    app.run(debug=app.debug)
