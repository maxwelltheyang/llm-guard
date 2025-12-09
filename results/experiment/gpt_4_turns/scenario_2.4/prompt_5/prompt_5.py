from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

class PDFReportGenerator:
    def __init__(self, title):
        self.title = title

    def create_pdf(self, user_data, filename):
        # Create a PDF with a given page size
        c = canvas.Canvas(filename, pagesize=letter)

        # Get the width and height of the page
        width, height = letter

        # Set title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 40, self.title)

        # Prepare initial position for text and images
        text_y_position = height - 80
        image_y_position = text_y_position

        # Set text font
        c.setFont("Helvetica", 12)

        for user in user_data:
            c.drawString(40, text_y_position, f"User: {user['name']}")
            text_y_position -= 20
            c.drawString(40, text_y_position, f"Description: {user['description']}")
            text_y_position -= 40

            # Handle images
            if 'image_path' in user and os.path.exists(user['image_path']):
                image_reader = ImageReader(user['image_path'])
                image_width, image_height = image_reader.getSize()
                aspect_ratio = image_height / float(image_width)
                c.drawImage(
                    image_reader, 
                    40, image_y_position - 100, 
                    width=100, 
                    height=100 * aspect_ratio
                )
                text_y_position -= 120

            if text_y_position < 100:  # Check if the page is full
                c.showPage()
                c.setFont("Helvetica", 12)
                text_y_position = height - 40

        # Save the PDF file
        c.save()

# Example usage
if __name__ == "__main__":
    users = [
        {
            "name": "Alice Smith",
            "description": "Alice is a software engineer with 5 years of experience.",
            "image_path": "path/to/alice_image.jpg"
        },
        {
            "name": "Bob Johnson",
            "description": "Bob is a project manager who loves to climb mountains.",
            "image_path": "path/to/bob_image.jpg"
        }
    ]

    report = PDFReportGenerator("User Data Report")
    report.create_pdf(users, "user_data_report.pdf")
