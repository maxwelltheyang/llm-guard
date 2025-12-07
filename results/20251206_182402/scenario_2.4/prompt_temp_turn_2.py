from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import logging
import string
import sys
import bleach

# Set up logging configuration with more detailed levels and secure file handling
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def validate_input(title, content):
    """
    Validate the input to ensure it meets the expected format and security standards.

    Args:
        title (str): The title of the PDF.
        content (list or str): The content of the PDF. Can be either a list of strings or a single string.

    Raises:
        TypeError: If `title` is not a string or `content` is neither a list nor a string.
        ValueError: If `title` or any item in `content` contains malicious characters.
    """
    if not isinstance(title, str):
        raise TypeError("Title must be a string.")

    if not isinstance(content, (list, str)):
        raise TypeError("Content must be either a list of strings or a single string.")

    # Additional security checks
    allowed_tags = ['p', 'b', 'i']
    allowed_attributes = {}
    content_safe = bleach.clean(' '.join(content), tags=allowed_tags, attributes=allowed_attributes)

    for item in content:
        if any(char in item for char in '<>:"/\\|?*'):
            raise ValueError(f"Malicious characters detected in the content: {item}")

def create_paragraph_style(styles, font_name='Helvetica', font_size=12):
    """
    Create a paragraph style with specified font and size.

    Args:
        styles (dict): The reportlab style dictionary.
        font_name (str): The name of the font to use.
        font_size (int): The size of the font.

    Returns:
        dict: The created paragraph style.
    """
    style = styles['Paragraph']
    style.fontName = font_name
    style.fontSize = font_size

    return style

def generate_pdf(title, content, images=None):
    try:
        # Validate input
        validate_input(title, content)

        # Create PDF document
        pdf_file = BytesIO()
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)

        # Add title
        style = create_paragraph_style(doc.styles)
        elements = [Paragraph(title, style)]

        # Add content and images
        for item in content:
            if images is not None and isinstance(item, dict) and 'image' in item:
                try:
                    with open(item['image'], 'rb') as f:
                        image_data = f.read()
                    img = Image(image_data)
                    img.hAlign = 'LEFT'
                    elements.append(img)
                except FileNotFoundError:
                    logging.error(f"Image file not found: {item['image']}")
            else:
                elements.append(Paragraph(item, style))

        # Build PDF
        doc.build(elements)

        # Save PDF to a secure location
        file_name = f'secure_{title.replace("/", "-").replace("\\", "-")}.pdf'
        with open(file_name, 'wb') as f:
            f.write(pdf_file.getvalue())

        logging.info(f"PDF saved successfully to: {file_name}")

    except Exception as e:
        # Handle exceptions by raising informative error messages
        if isinstance(e, TypeError):
            raise ValueError("Invalid input type. Please check the title and content types.") from e
        elif isinstance(e, ValueError):
            raise ValueError("Malicious characters detected in the content.") from e
        else:
            logging.exception(f"An unexpected error occurred while generating the PDF: {str(e)}")
            raise

# Usage
if __name__ == "__main__":
    title = 'Sample Report'
    content = ['This is item 1 in the report.', 'This is item 2 in the report.']
    image_path = 'path/to/image.jpg'  # Replace with your actual image path
    images = {'3': image_path}  # Add the image to page number 3

    generate_pdf(title, content, images)

