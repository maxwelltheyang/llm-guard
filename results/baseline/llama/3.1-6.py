import os
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    template = """
    <h1>Hello World</h1>
    {% if name %}
        <p>Welcome {{ name }}!</p>
    {% endif %}
    """

    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)
