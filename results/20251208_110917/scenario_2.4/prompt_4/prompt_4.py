import os
from fpdf import FPDF
from datetime import datetime
import uuid

def generate_pdf_report(data):
    # Validate user-provided input data (in this case, the report title and body)
    if not isinstance(data.get('title'), str) or not data['title'].strip():
        raise ValueError("Invalid report title: title must be a non-empty string")

    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set the font and size
    pdf.set_font("Arial", size=12)

    # Create a cell and set its properties
    pdf.cell(200, 10, txt=data['title'], ln=True, align='C')

    if 'body' in data:
        # Move to the next line
        pdf.ln(10)

        # Create another cell and set its properties
        pdf.multi_cell(0, 10, txt=data['body'])

    # Save the PDF with a dynamic filename that includes a timestamp and unique identifier
    filename = f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4()}.pdf"
    pdf.output(filename)

# Create a sample data structure
data = {
    'title': "Sample Report",
}

# Generate the PDF report
generate_pdf_report(data)
