from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import logging
import string
import sys
import bleach
import os

# Set up logging configuration with more detailed levels and secure file handling
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('pdf_generator.log'),
        logging.StreamHandler()
    ]
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
    Create a paragraph style with the specified font and size.

    Args:
        styles (reportlab.lib.styles.Style): The reportlab styles object.
        font_name (str): The font name to use. Defaults to 'Helvetica'.
        font_size (int): The font size to use. Defaults to 12.

    Returns:
        reportlab.lib.styles.Style: The created paragraph style.
    """
    try:
        style = styles['BodyText']
        style.fontName = font_name
        style.fontSize = font_size
        return style
    except Exception as e:
        logging.exception(f"An error occurred while creating the paragraph style: {str(e)}")
        raise

def save_pdf(file_path, pdf_bytes):
    """
    Save the PDF to the specified file path.

    Args:
        file_path (str): The file path where the PDF will be saved.
        pdf_bytes (bytes): The bytes representing the PDF content.
    """
    try:
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
    except Exception as e:
        logging.exception(f"An error occurred while saving the PDF: {str(e)}")
        raise

def generate_pdf(title, content, image_paths=None):
    """
    Generate a PDF with the specified title and content.

    Args:
        title (str): The title of the PDF.
        content (list or str): The content of the PDF. Can be either a list of strings or a single string.
        image_paths (dict, optional): A dictionary mapping page numbers to image paths. Defaults to None.

    Raises:
        TypeError: If `title` is not a string or `content` is neither a list nor a string.
        ValueError: If `title` or any item in `content` contains malicious characters.
    """
    try:
        if image_paths and not isinstance(image_paths, dict):
            raise ValueError("Image paths must be a dictionary")

        # Validate input
        validate_input(title, content)

        # Create PDF
        doc = SimpleDocTemplate('pdf_report.pdf')
        styles = getSampleStyleSheet()
        style = create_paragraph_style(styles)

        elements = []
        for item in content:
            if isinstance(item, str):
                elements.append(Paragraph(item, style))
            elif isinstance(item, dict) and 'image' in item:
                try:
                    image_path = os.path.abspath(item['image'])
                    elements.append(Image(image_path))
                except Exception as e:
                    logging.exception(f"An error occurred while adding an image: {str(e)}")
        if image_paths:
            for page_number, image_path in image_paths.items():
                try:
                    image_path = os.path.abspath(image_path)
                    elements.insert(int(page_number), Image(image_path))
                except Exception as e:
                    logging.exception(f"An error occurred while adding an image on page {page_number}: {str(e)}")

        doc.build(elements)

        # Save PDF
        file_name = f'secure_{title.replace("/", "-").replace("\\", "-")}.pdf'
        save_pdf(file_name, doc)
    except Exception as e:
        logging.exception(f"An unexpected error occurred while generating the PDF: {str(e)}")
        raise

# Usage
if __name__ == "__main__":
    title = 'Sample Report'
    content = ['This is item 1 in the report.', 'This is item 2 in the report.']
    image_path = '/path/to/image.jpg'  # Replace with your actual image path
    image_paths = {'3': image_path}  # Add the image to page number 3

    generate_pdf(title, content, image_paths)

