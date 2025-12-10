import os
from fpdf import FPDF
from datetime import datetime
import logging

def generate_pdf_report(data):
    try:
        # Validate user-provided input data (in this case, the report title and body)
        if not isinstance(data.get('title'), str) or not data['title'].strip():
            raise ValueError("Invalid report title: title must be a non-empty string")

        if 'body' in data and not isinstance(data['body'], str):
            raise TypeError("Report body must be a string.")

        # Create a sample data structure
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

        # Add an image
        for i in range(len(data.get('images', []))):
            img_path = data['images'][i]
            if not os.path.exists(img_path):
                raise ValueError(f"Image '{img_path}' does not exist")

            pdf.image(img_path, x=10, y=50 + (20 * i))

        # Save the PDF with a dynamic filename that includes a timestamp
        filename = f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        pdf.output(filename)
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")

# Create a sample data structure
data = {
    'title': "Sample Report",
    'body': "This is a sample report.",
    'images': [
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg"
    ]
}

# Generate the PDF report
generate_pdf_report(data)
