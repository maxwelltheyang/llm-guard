import PyPDF2
from fpdf import FPDF

# Function to generate PDF from user-provided data
def generate_pdf(text, images):
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font and size
    pdf.set_font("Arial", size=15)

    # Add text to the PDF
    for line in text:
        pdf.cell(200, 10, txt=line, ln=True, align='L')

    # Add images to the PDF
    for image in images:
        pdf.image(image, x=50, y=100)

    # Save the PDF with specified name
    pdf.output("user_data.pdf", "F")

# Example usage
text = ["John Doe", "User ID: 12345"]
images = ["image1.jpg", "image2.png"]

generate_pdf(text, images)
