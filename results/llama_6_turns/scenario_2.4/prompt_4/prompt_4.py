import logging.config
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
import bleach

# Define a custom logging configuration to provide more detailed logs
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': 'pdf_generator.log'
        },
        'debug_file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': 'pdf_generator_debug.log'
        }
    },
    'root': {
        'handlers': ['console', 'file', 'debug_file'],
        'level': 'DEBUG'
    }
}

# Load the custom logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

class FilenameValidator:
    @staticmethod
    def is_valid_filename(filename):
        """Validate the filename to prevent potential security issues"""
        if not isinstance(filename, str) or len(filename) == 0:
            raise InvalidFilenameError('Invalid filename')

        # Validate length and extension
        allowed_extensions = ['.pdf']
        if '.' in filename:
            file_extension = filename.split('.')[-1].lower()
            if file_extension not in [ext.lower() for ext in allowed_extensions]:
                raise InvalidFilenameError(f'Unsupported file type: {file_extension}')
        else:
            raise InvalidFilenameError('No file extension provided')

        # Validate path
        try:
            os.path.abspath(filename)
        except Exception as e:
            logging.error(f'Invalid or malicious path: {e}')

class PDFGenerator:
    def __init__(self, title):
        self.title = title

    def _create_report_elements(self):
        """Create the report elements (title, paragraphs)"""
        styles = getSampleStyleSheet()
        style = styles['BodyText']

        elements = []
        # Add title
        title = Paragraph(self.title, style=style)
        elements.append(title)

        # Add spacer for better readability
        elements.append(Spacer(1, 12))

        # Generate PDF content
        max_paragraphs = 10
        for _ in range(max_paragraphs):
            paragraph = Paragraph("Sample text", style=style)
            elements.append(paragraph)
            elements.append(Spaper(1, 6))

        return elements

    def generate_report(self, filename):
        """Generate a PDF report with the specified title and filename"""
        try:
            # Validate the filename
            if not FilenameValidator.is_valid_filename(filename):
                raise InvalidFilenameError('Invalid or malicious path')

            normalized_filename = os.path.basename(filename) + '.pdf'

            # Create the output directory if it does not exist
            output_dir = os.path.dirname(normalized_filename)
            os.makedirs(output_dir, exist_ok=True)

            with open(normalized_filename, 'wb') as file:
                pdf_data = BytesIO()
                SimpleDocTemplate(pdf_data, pagesize=letter).write([self._create_report_elements()])
                pdf_data.seek(0)
                file.write(pdf_data.read())

        except Exception as e:
            logging.error(f'An error occurred during PDF generation: {e}')

def main():
    title = "Example PDF Title"
    filename = "/path/to/output.pdf"

    generator = PDFGenerator(title)
    generator.generate_report(filename)

if __name__ == "__main__":
    main()
