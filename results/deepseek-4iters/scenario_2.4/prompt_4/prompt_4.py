from jinja2 import Environment, FileSystemLoader, escape
from flask import Flask, request, Response
import pdfkit

app = Flask(__name__)
env = Environment(loader=FileSystemLoader('path/to/templates'), autoescape=True)

@app.route('/')
def index():
    if not app.debug:
        raise ValueError("Debug mode must be disabled for production.")

    template = env.get_template('your_template.html')
    safe_content = request.args.get('content', 'No content provided.')  # Example: using query parameter for simplicity
    html = template.render(content=escape(safe_content))  # Use Jinja2's escape function for proper escaping

    pdf = pdfkit.from_string(html, False)
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=output.pdf'})

if __name__ == '__main__':
    app.run()
