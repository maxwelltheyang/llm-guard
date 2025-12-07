import io
from fpdf import FPDF  # For generating PDF

def generate_pdf():
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font and size
    pdf.set_font("Arial", size=15)

    # Create a text cell
    pdf.cell(200, 10, txt="Hello World!", ln=True, align='C')

    # Output the PDF with desired name
    pdf.output("hello_world.pdf")

generate_pdf()
