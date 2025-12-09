from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFReportGenerator:
    def __init__(self, title):
        self.title = title

    def create_pdf(self, content, filename):
        # Create a PDF with a given page size
        c = canvas.Canvas(filename, pagesize=letter)

        # Get the width and height of the page
        width, height = letter

        # Set title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 40, self.title)

        # Prepare content
        c.setFont("Helvetica", 12)
        text = c.beginText(40, height - 80)
        text.setTextOrigin(40, height - 80)
        text.setLeading(15)  # Line spacing
        text.textLines(content)

        # Add content to the PDF
        c.drawText(text)

        # Save the PDF file
        c.save()

# Example usage
if __name__ == "__main__":
    report = PDFReportGenerator("Monthly Report")
    report_content = (
        "January Report\n"
        "==============\n"
        "Summary:\n"
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    )
    report.create_pdf(report_content, "monthly_report.pdf")
