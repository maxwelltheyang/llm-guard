from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import logging
import string
import sys

# Set up logging configuration with more detailed levels
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def validate_input(title, content):
    """
    Validate the input to ensure it meets the expected format.

    Args:
        title (str): The title of the PDF.
        content (list or str): The content of the PDF. Can be either a list of strings or a single string.

    Raises:
        TypeError: If `title` is not a string or `content` is neither a list nor a string.
    """
    if not isinstance(title, str):
        raise TypeError("Title must be a string.")

    if not isinstance(content, (list, str)):
        raise TypeError("Content must be either a list of strings or a single string.")

def create_paragraph_style(styles, font_name='Helvetica-Bold', font_size=24):
    """
    Create a custom paragraph style.

    Args:
        styles: The reportlab styles dictionary.
        font_name (str): The name of the font. Defaults to 'Helvetica-Bold'.
        font_size (int): The size of the font. Defaults to 24.

    Returns:
        ParagraphStyle: A custom paragraph style object.
    """
    return ParagraphStyle(name='Title', fontName=font_name, fontSize=font_size)

def generate_pdf(title, content):
    """
    Generate a PDF from scratch without relying on third-party libraries.

    Args:
        title (str): The title of the PDF.
        content (list or str): The content of the PDF. Can be either a list of strings or a single string.

    Returns:
        bytes: The generated PDF as bytes, or None if an error occurs during generation.
    """
    try:
        validate_input(title, content)

        styles = getSampleStyleSheet()
        style = create_paragraph_style(styles)
        style.alignment = 'center'  # Fix alignment issue

        if isinstance(content, str):
            content_list = [content]
        else:
            content_list = content

        element_list = []

        # Add title
        paragraph = Paragraph(title, style)
        element_list.append(paragraph)

        # Add content
        for item in content_list:
            paragraph = Paragraph(item, styles['BodyText'])
            element_list.append(paragraph)

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        try:
            doc.build(element_list)
        except OSError as e:
            logging.error(f"Error generating PDF: {str(e)}")
            return None
        else:
            logging.info("PDF generated successfully.")
            return pdf_buffer.getvalue()

    except Exception as e:
        # Handle exceptions by logging or raising informative error messages
        if isinstance(e, TypeError):
            logging.warning(f"Invalid input type. Please check the title and content types: {str(e)}.")
        elif isinstance(e, OSError):
            logging.error(f"Error generating PDF: {str(e)}")
        else:
            logging.exception(f"An unexpected error occurred while generating the PDF: {str(e)}.")

# Usage
if __name__ == "__main__":
    title = 'Sample Report'
    content = ['This is item 1 in the report.', 'This is item 2 in the report.']
    generated_pdf = generate_pdf(title, content)

    if generated_pdf:
        with open('sample.pdf', 'wb') as f:
            f.write(generated_pdf)
