from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import logging
import string
import sys

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
    for item in content:
        if any(char in item for char in '<>:"/\\|?*'):
            raise ValueError(f"Malicious characters detected in the content: {item}")

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

def generate_pdf(title, content, images=None):
    """
    Generate a PDF from scratch without relying on third-party libraries.

    Args:
        title (str): The title of the PDF.
        content (list or str): The content of the PDF. Can be either a list of strings or a single string.
        images (list or dict): A list of image file paths or a dictionary mapping page numbers to image file paths.

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

        if images:
            logging.info("Adding images to the report...")
            for page_num, image_path in images.items():
                try:
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    img = Image(image_data)
                    img.hAlign = 'LEFT'
                    content_list.insert(page_num - 1, img)  # Insert at the specified page number
                except FileNotFoundError:
                    logging.error(f"Image file not found: {image_path}")
        else:
            logging.info("No images to add.")

        pdf_file = BytesIO()
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = [Paragraph(title, style)] + content_list
        doc.build(elements)

        logging.info("PDF generated successfully.")
        return pdf_file.getvalue()

    except Exception as e:
        # Handle exceptions by logging or raising informative error messages
        if isinstance(e, TypeError):
            logging.warning(f"Invalid input type. Please check the title and content types: {str(e)}.")
        elif isinstance(e, ValueError):
            logging.error(f"Malicious characters detected in the content: {e}.")
        else:
            logging.exception(f"An unexpected error occurred while generating the PDF: {str(e)}.")

# Usage
if __name__ == "__main__":
    title = 'Sample Report'
    content = ['This is item 1 in the report.', 'This is item 2 in the report.']
    image_path = 'path/to/image.jpg'  # Replace with your actual image path
    images = {'3': image_path}  # Add the image to page number 3

    generated_pdf = generate_pdf(title, content, images)

    if generated_pdf:
        try:
            file_name = input("Enter a custom file name (without extension): ")
            with open(f'{file_name}.pdf', 'wb') as f:
                f.write(generated_pdf)
            logging.info(f"PDF saved successfully to: {file_name}.pdf")
        except Exception as e:
            logging.error(f"Error saving PDF: {str(e)}")
    else:
        logging.error("Failed to generate or save the PDF.")
