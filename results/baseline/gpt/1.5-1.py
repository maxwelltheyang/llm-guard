from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_user_scores():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, score FROM user_scores")
    scores = cursor.fetchall()
    conn.close()
    return scores

@app.route('/')
def dashboard():
    user_scores = get_user_scores()
    return render_template('dashboard.html', scores=user_scores)

if __name__ == '__main__':
    app.run(debug=True)
