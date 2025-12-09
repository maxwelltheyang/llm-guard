from fpdf import FPDF
from flask import Flask, send_file, make_response
import io
import os

app = Flask(__name__)

class PDF(FPDF):
    def header(self):
        # Insert a header
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Python Web App PDF Report', 0, 1, 'C')

    def footer(self):
        # Page numbers
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

@app.route('/generate_report')
def generate_report():
    # Create a PDF object
    pdf = PDF()
    pdf.add_page()

    # Add some content to the PDF
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, "This is a sample report generated without using third-party libraries.", 0, 1)

    # Create a BytesIO object and output the PDF to it
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)

    # Set the buffer position to the beginning
    pdf_buffer.seek(0)

    # Prepare the response to send the PDF back to the user
    response = make_response(send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, attachment_filename='report.pdf'))
    response.headers['Content-Disposition'] = 'inline; filename=report.pdf'

    return response

if __name__ == '__main__':
    # Use an environment variable to configure debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
