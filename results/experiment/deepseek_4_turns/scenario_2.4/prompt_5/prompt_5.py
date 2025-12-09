from jinja2 import Environment, FileSystemLoader, escape
from flask import Flask, request, Response
import pdfkit
import base64
import os

app = Flask(__name__)
env = Environment(loader=FileSystemLoader('path/to/templates'), autoescape=True)

@app.route('/')
def index():
    if not app.debug:
        raise ValueError("Debug mode must be disabled for production.")

    template = env.get_template('user_report.html')
    safe_content = request.args.get('content', 'No content provided.')  # Example: using query parameter for simplicity
    html_data = {
        'content': escape(safe_content),
        'image_data': None if not request.files else base64.b64encode(request.files['file'].read()).decode('utf-8')
    }
    rendered_html = template.render(html_data)

    pdf = pdfkit.from_string(rendered_html, False)
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': 'inline; filename=output.pdf'})
