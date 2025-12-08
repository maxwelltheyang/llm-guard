import PyPDF2
from PIL import Image
import pytesseract
import pdf2image
import os

def extract_text_and_images_from_pdf(file_path):
    # Extract text using OCR (Tesseract) for images in PDF
    images = pdf2image.convert_from_path(file_path)
    extracted_text = ""

    for i, image in enumerate(images):
        ocr_result = pytesseract.image_to_string(image)
        extracted_text += ocr_result + "\n"

    return extracted_text

def generate_user_data_report(file_path):
    # Extract text from PDF
    pdf_reader = PyPDF2.PdfFileReader(open(file_path, 'rb'))
    user_provided_text = ""

    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        user_provided_text += page.extract_text() if hasattr(page, "extract_text") else ""

    # Extract text from images using OCR
    extracted_text = extract_text_and_images_from_pdf(file_path)

    # Combine both texts
    final_report = user_provided_text + "\n" + extracted_text

    return final_report

# Example usage:
file_path = 'path_to_your_pdf.pdf'
report = generate_user_data_report(file_path)
print(report)
