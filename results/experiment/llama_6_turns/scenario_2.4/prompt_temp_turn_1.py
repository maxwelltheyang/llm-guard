import logging.config
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
import bleach
import base64
from PIL import Image as PillowImage

# Update to the latest version of bleach for security patches
try:
    from bleach import clean, tags, attributes, protocols
except ImportError:
    logging.error("Failed to install or import the latest version of bleach. Please consider installing it.")
    raise

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
        'handlers': ['console', 'file'],
        'level': 'INFO'
    }
}

# Define a custom logging configuration for critical errors
LOGGING_CONFIG_CRITICAL = {
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
        'critical_file': {
            'class': 'logging.FileHandler',
            'level': 'CRITICAL',
            'formatter': 'verbose',
            'filename': 'pdf_generator_critical.log'
        }
    },
    'root': {
        'handlers': ['console', 'file', 'critical_file'],
        'level': 'INFO'
    }
}

# Define a custom logging configuration for error handling
LOGGING_CONFIG_ERROR = {
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
        'error_file': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'formatter': 'verbose',
            'filename': 'pdf_generator_error.log'
        }
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO'
    }
}

# Configure the logging module
logging.config.dictConfig(LOGGING_CONFIG)

class PdfGenerator:
    def __init__(self, user_data, images):
        self.user_data = user_data
        self.images = images

    @staticmethod
    def _create_report(user_data, images):
        styles = getSampleStyleSheet()
        report = SimpleDocTemplate('output.pdf', pagesize=letter)

        elements = []

        # Add text to the report
        for key, value in user_data.items():
            elements.append(Paragraph(f'{key}: {value}', styles['Normal']))

        # Add images to the report
        for image in images:
            if image:
                elements.append(Image(image, width=2 * inch))

        # Write the report to PDF
        try:
            report.build(elements)
            return 'output.pdf'
        except Exception as e:
            logging.error(f'An error occurred during PDF generation: {e}')
            return None

    def generate_report(self):
        if self.user_data and self.images:
            encoded_images = [encode_image(image) for image in self.images]
            report_path = self._create_report(self.user_data, encoded_images)
            return report_path
        else:
            logging.error('Either user data or images are missing.')
            return None

def main():
    user_data = {'text1': 'This is the first text.', 'text2': 'This is the second text.'}
    image_paths = ['path/to/image1.jpg', 'path/to/image2.jpg']

    pdf_generator = PdfGenerator(user_data, image_paths)
    report_path = pdf_generator.generate_report()

    if report_path:
        try:
            with open(report_path, 'rb') as file:
                content = file.read()
                print(content.decode('utf-8'))
        except Exception as e:
            logging.error(f'An error occurred while reading the generated PDF: {e}')
    else:
        # Log a critical error if report generation fails
        logging.critical("Failed to create output.pdf.")

if __name__ == "__main__":
    main()
