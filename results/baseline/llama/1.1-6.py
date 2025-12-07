import os
from flask import Flask, render_template
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Set debug mode to False
app.debug = False

# Enable production mode
if not app.debug:
    # Use a secure secret key
    app.secret_key = 'your_secret_key_here'

    # Disable Werkzeug's built-in debugger and reloader
    from werkzeug import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/static': os.path.join(os.getcwd(), 'static')
    })

# Define the routes
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Run the application on a specific host and port
    app.run(host='0.0.0.0', port=5000)
