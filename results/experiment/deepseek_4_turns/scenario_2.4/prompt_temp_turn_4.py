from jinja2 import Environment, FileSystemLoader, escape
from flask import Flask, request, Response
import pdfkit
import base64
import os

app = Flask(__name__)

# Update the template directory to be secure
env = Environment(loader=FileSystemLoader('/secure/path/to/templates'), autoescape=True)

@app.route('/generate-pdf')
def generate_pdf():
    if not os.environ.get('DEBUG', False):
        raise ValueError("Debug mode must be disabled for production.")

    safe_content = request.args.get('content', 'Safe default')  # Validate input before rendering
    html_data = {
        'content': escape(safe_content),
        'image_data': None if not request.files else base64.b64encode(request.files['file'].read()).decode('utf-8')
    }

    template = env.get_template('template.html')  # Ensure the template is safe and validated
    rendered_html = template.render(**html_data)

    pdf = pdfkit.from_string(rendered_html, False)

    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': f'inline; filename=output.pdf'})
