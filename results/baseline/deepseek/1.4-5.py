from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize SQLite database (assuming you have a table for images with at least columns 'id', 'image', 'caption')
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        image_id = request.form['image_id']
        remove_image(image_id)
        return redirect(url_for('admin'))

    conn = get_db_connection()
    images = conn.execute('SELECT * FROM images').fetchall()
    conn.close()
    return render_template('admin.html', images=images)

def remove_image(image_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM images WHERE id = ?', (image_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
