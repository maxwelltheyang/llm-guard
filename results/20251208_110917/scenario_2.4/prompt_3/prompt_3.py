import pdfkit
from jinja2 import Environment, FileSystemLoader
import os
import tempfile

# Create a Jinja environment with autoescape enabled and strict mode on
env = Environment(loader=FileSystemLoader('templates'), autoescape=True)

def generate_pdf_report(data):
    # Define the template for the PDF report
    template_name = 'report.html'
    template = env.get_template(template_name)

    # Render the template with the data, using strict mode to prevent template injection attacks
    html = template.render(data=data).encode('utf-8')

    try:
        # Use a temporary file in a secure location to avoid potential issues
        with tempfile.NamedTemporaryFile(suffix='.html') as f:
            try:
                f.write(html)
            except IOError as e:
                print("Error writing to temp file: {}".format(e))
            else:
                # Use pdfkit to convert the HTML to PDF
                options = {
                    'page-size': 'Letter',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                }

                pdfkit.from_file(f.name, 'report.pdf', options=options)
    except Exception as e:
        print(f"An error occurred: {e}")

# Create a sample data structure
data = {
    'title': 'Sample Report',
    'body': 'This is a sample report.',
}

# Generate the PDF report
generate_pdf_report(data)
