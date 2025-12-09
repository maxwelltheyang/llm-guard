from fpdf import FPDF
from flask import Flask, request, send_file, make_response, abort
import io
import os
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'User Data Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def validate_and_decode_image(encoded_image):
    try:
        # Ensure the image is a valid base64 string and not too large
        if len(encoded_image) > 10 * 1024 * 1024:  # Limit size to 10 MB
            raise ValueError("Image is too large")
        return base64.b64decode(encoded_image)
    except Exception as e:
        logging.error("Error decoding image: %s", str(e))
        raise

@app.route('/generate_report', methods=['POST'])
def generate_report():
    if not request.is_json:
        abort(400, description="Invalid input, expecting JSON")

    # Simple text validation
    data = request.json.get('text', '')
    if len(data) > 5000:  # Limit text length to 5000 characters
        abort(400, description="Text is too long")

    images = request.json.get('images', [])
    validated_images = []

    for img_data in images:
        try:
            validated_images.append(validate_and_decode_image(img_data))
        except ValueError as e:
            abort(400, description=str(e))

    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    pdf.multi_cell(0, 10, data)

    for image_bytes in validated_images:
        try:
            image_stream = io.BytesIO(image_bytes)
            pdf.add_page()
            pdf.image(image_stream, x=10, y=30, w=pdf.w - 20)
        except Exception as e:
            # Log the exact cause on the server for debugging
            logging.error("Error processing image for PDF: %s", str(e))
            continue

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    response = make_response(send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, attachment_filename='user_report.pdf'))
    response.headers['Content-Disposition'] = 'inline; filename=user_report.pdf'

    # Add security-related headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'

    return response

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ['true', '1', 't']
    app.run(debug=debug_mode)
