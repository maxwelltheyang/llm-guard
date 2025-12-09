from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    data = {'message': 'Hello, World!'}
    return render_template('index.html', **data)

if __name__ == '__main__':
    app.run(debug=False)
