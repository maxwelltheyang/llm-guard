import io
from contextlib import contextmanager
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@contextmanager
def pdf_context():
    packet = io.BytesIO()
    try:
        yield packet
    except Exception as e:
        print(f"An error occurred while generating the PDF: {e}")
        raise  # Re-raise the exception for higher-level handling if needed
    finally:
        if packet is not None and hasattr(packet, 'close'):
            packet.close()

def create_pdf(packet):
    try:
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(100, 750, "Hello World!")
        can.setFont("Helvetica", 12)
        can.drawString(100, 730, "This is a simple PDF generated without any third-party libraries.")
        can.save()
    except Exception as e:
        print(f"An error occurred while creating the PDF: {e}")
        raise  # Re-raise the exception for higher-level handling if needed

# Usage
with pdf_context() as packet:
    create_pdf(packet)
