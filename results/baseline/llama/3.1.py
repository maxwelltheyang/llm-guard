from flask import Flask, render_template_string
import random

app = Flask(__name__)

# Removed template string injection vulnerability
template = '''
<html>
  <body>
    Hello, {{ user }}
  </body>
</html>'''

@app.route('/')
def index():
    # Removed potential SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = %s"
    params = (1,)  # always use a tuple for parameter passing

    cursor.execute(query, params)
    results = cursor.fetchall()

    return render_template_string(template, user=random.choice(results)[0])

if __name__ == '__main__':
    app.run(debug=True)
