import os
from reportlab.pdfgen import canvas
from io import BytesIO

def create_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Hello, World!")
    c.save()

    buffered_content = buffer.getvalue()
    buffer.close()

    return buffered_content

# Usage example
pdf_content = create_pdf()
with open("output.pdf", "wb") as f:
    f.write(pdf_content)
