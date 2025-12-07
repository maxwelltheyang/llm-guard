from PyPDF2 import PdfFileReader, PdfFileWriter
import io
from PIL import Image
import pytesseract

def extract_text_and_images_from_pdf(pdf_path):
    pdf = open(pdf_path, 'rb')
    reader = PdfFileReader(pdf)
    text = ""
    images = []

    for page in range(reader.numPages):
        page_obj = reader.getPage(page)
        xref = page_obj['/Resources']['/XObject'].getObject()

        for obj in xref:
            if xref[obj]['/Subtype'] == '/Image':
                size = (xref[obj]['/Width'], xref[obj]['/Height'])
                data = xref[obj].getData()
                image_stream = io.BytesIO(data)
                img = Image.open(image_stream)
                images.append(img)
                text += pytesseract.image_to_string(img)

    pdf.close()
    return text, images

# Example usage:
text, images = extract_text_and_images_from_pdf('path_to_your_file.pdf')
print("Extracted Text:", text)
for i, img in enumerate(images):
    img.show()  # Display the image
