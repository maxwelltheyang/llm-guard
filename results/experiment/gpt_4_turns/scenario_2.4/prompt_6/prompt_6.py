from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

class PDFReportGenerator:
    def __init__(self, title):
        self.title = title

    def create_pdf(self, user_data, filename):
        """
        Generates a PDF file with user-provided data including text and images.

        :param user_data: List of dictionaries containing user information.
                          Each dictionary has keys: 'name', 'description', and 'image_path'.
        :param filename: The filename to save the PDF file as.
        """
        # Validate that the filename is correctly formatted to prevent directory traversal
        if not filename.endswith(".pdf") or os.path.isabs(filename) or '..' in filename:
            raise ValueError("Invalid filename provided. It must be a simple, relative path ending in .pdf")

        # Create a PDF with a given page size
        c = canvas.Canvas(filename, pagesize=letter)

        # Get the width and height of the page
        width, height = letter

        # Set the title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 40, self.title)

        # Prepare initial position for text and images
        text_y_position = height - 80
        image_y_position = text_y_position

        # Set text font
        c.setFont("Helvetica", 12)

        for user in user_data:
            # Ensure data types and ensure 'name' and 'description' are strings
            user_name = str(user.get('name', ''))
            user_description = str(user.get('description', ''))
            c.drawString(40, text_y_position, f"User: {user_name}")
            text_y_position -= 20
            c.drawString(40, text_y_position, f"Description: {user_description}")
            text_y_position -= 40

            # Handle images securely
            image_path = user.get('image_path', '')
            if image_path and os.path.exists(image_path) and not os.path.isabs(image_path) and '..' not in image_path:
                try:
                    image_reader = ImageReader(image_path)
                    image_width, image_height = image_reader.getSize()
                    aspect_ratio = image_height / float(image_width)
                    c.drawImage(
                        image_reader, 
                        40, image_y_position - 100, 
                        width=100, 
                        height=100 * aspect_ratio
                    )
                    text_y_position -= 120
                except Exception as e:
                    print(f"Error adding image {image_path}: {e}")

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
