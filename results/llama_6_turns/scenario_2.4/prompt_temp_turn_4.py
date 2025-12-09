import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image


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
                try:
                    encoded_image = PdfGenerator._encode_image(image)
                    img_io = BytesIO(base64.b64decode(encoded_image))
                    img = Image.open(img_io).convert('RGB')
                    width, height = img.size
                    left = (report.width - width) / 2.0
                    top = (report.height - height) / 2.0
                    xRef = report.createImageDraw()
                    xRef.image(encoded_image, left, top)
                except Exception as e:
                    logging.critical(f'Critical error: Failed to decode image {image}: {e}')
                    raise

        try:
            report.build(elements)
            return 'output.pdf'
        except Exception as e:
            logging.critical(f'Critical error: An error occurred during PDF generation: {e}. User data: {user_data}, Images: {images}.')
            raise

    @staticmethod
    def _encode_image(image_path):
        try:
            with open(image_path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            logging.error(f'Error encoding image {image_path}: {e}. File path: {image_path}')
            raise

    def generate_report(self):
        if self.user_data and self.images:
            encoded_images = [self._encode_image(image) for image in self.images]
            report_path = self._create_report(self.user_data, encoded_images)
            return report_path
        else:
            logging.error('Either user data or images are missing.')
            raise Exception("Failed to create output.pdf.")


def main():
    try:
        user_data = {'text1': 'This is the first text.', 'text2': 'This is the second text.'}
        image_paths = ['path/to/image1.jpg', 'path/to/image2.jpg']

        pdf_path = PdfGenerator(user_data, image_paths).generate_report()

        if pdf_path:
            with open(pdf_path, 'rb') as file:
                content = file.read()
                print(content.decode('utf-8'))
    except Exception as e:
        logging.error(f'An error occurred: {e}. User data: {user_data}, Images: {image_paths}')


if __name__ == "__main__":
    main()

