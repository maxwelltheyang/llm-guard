import os
from fpdf import FPDF
from datetime import datetime, timezone
import logging
from typing import Dict

# Configure logging to avoid sensitive data leaks
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def generate_pdf_report(data: Dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("Invalid input data")

    required_fields = ['title', 'body']
    optional_fields = ['images']

    for field in required_fields + optional_fields:
        if field not in data:
            logger.error(f"Missing required field '{field}'")
            raise ValueError(f"Missing required field '{field}'")

        if field == 'title':
            if not isinstance(data[field], str) or not data[field].strip():
                logger.error("Invalid report title: title must be a non-empty string")
                raise ValueError("Invalid report title: title must be a non-empty string")
        elif field == 'body' and data[field] is not None:
            if not isinstance(data[field], str):
                logger.error("Report body must be a string.")
                raise TypeError("Report body must be a string.")
        elif field == 'images':
            for i, img_path in enumerate(data.get('images', [])):
                if not os.path.exists(img_path):
                    logger.error(f"Image '{img_path}' does not exist")
                    raise ValueError(f"Image '{img_path}' does not exist")
                if not img_path.endswith(('.jpg', '.jpeg', '.png')):
                    logger.error(f"Invalid image type for image '{img_path}'")
                    raise ValueError(f"Invalid image type for image '{img_path}'")

    try:
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
            pdf.image(img_path, x=10, y=50 + (20 * i))

        # Save the PDF with a dynamic filename that includes a timestamp
        current_time = datetime.now(tz=timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f"report_{current_time}.pdf"
        pdf.output(filename)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise

# Create a sample data structure
data = {
    'title': "Sample Report",
    'body': "This is a sample report.",
    'images': [
        "/path/to/image1.jpg",
        "/path/to/image2.png"
    ]
}

try:
    generate_pdf_report(data)
except Exception as e:
    logger.error(f"Error generating report: {str(e)}")
