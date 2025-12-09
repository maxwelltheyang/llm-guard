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
        """Validate a filename to prevent malicious paths"""
        return os.path.basename(filename) != '' and not any(char in '<>:"/\\|?*' for char in filename)

class DirectoryCreator:
    """Class for handling directory creation with error handling"""

    @staticmethod
    def create_directory(path):
        try:
            # Allow the directory to be created if it already exists, but log exceptions for permission issues
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logging.error(f"Failed to create directory: {e}")

def sanitize_user_input(user_data):
    """Sanitize user input using bleach"""
    try:
        # Use the latest version of bleach
        from bleach import clean, tags, attributes, protocols
        clean_kwargs = {
            'tags': tags.sanitizer_allowed_tags,
            'attributes_function': lambda tag: attributes.sanitizer_allowed_attrs.get(tag, []),
            'protocols': [p for p in protocols.sanitizer_allowed_protocols if p not in ['javascript', 'vbscript']],
            'strip': True
        }
        return {key: clean(value, **clean_kwargs) for key, value in user_data.items()}
    except ImportError:
        # Handle the case where bleach is not installed or imported successfully
        logging.error("Failed to import bleach")
        raise

def encode_image(image_path):
    """Encode an image using base64"""
    retry_count = 0
    max_retries = 3
    while retry_count <= max_retries:
        try:
            # Open the image file and read its content in binary format
            with open(image_path, 'rb') as image_file:
                encoded_image_data = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_image_data
        except Exception as e:
            retry_count += 1
            if retry_count <= max_retries:
                logging.warning(f"Failed to encode image after {retry_count} retries: {str(e)}")
            else:
                # Raise an exception when the maximum number of retries is reached
                logging.critical(f"Failed to encode image after {max_retries} retries: {str(e)}")
                raise

def main():
    user_data = {'text1': 'This is the first text.', 'text2': 'This is the second text.'}
    image_path1 = 'path/to/image1.jpg'
    image_path2 = 'path/to/image2.jpg'

    sanitized_user_data = sanitize_user_input(user_data)
    images = [encode_image(image_path1), encode_image(image_path2)]

    if all(images):
        try:
            with open('output.pdf', 'wb') as file:
                file.write(_create_report(sanitized_user_data, images))
        except Exception as e:
            logging.error(f'An error occurred during PDF generation: {e}')
    else:
        # If any image failed to encode, log a critical error
        logging.critical("Failed to create output.pdf.")

if __name__ == "__main__":
    main()
