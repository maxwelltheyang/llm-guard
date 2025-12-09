from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFReportGenerator:
    def __init__(self, title, filename):
        self.title = title
        self.filename = filename
        self.canvas = canvas.Canvas(self.filename, pagesize=letter)
        self.width, self.height = letter
        self.setup_pdf()

    def setup_pdf(self):
        self.canvas.setFont("Helvetica-Bold", 16)
        self.canvas.drawCentredString(self.width / 2, self.height - 40, self.title)

    def add_section(self, heading, text, y_position):
        self.canvas.setFont("Helvetica-Bold", 12)
        self.canvas.drawString(72, y_position, heading)

        self.canvas.setFont("Helvetica", 12)
        text_object = self.canvas.beginText(72, y_position - 14)
        text_object.setTextOrigin(72, y_position - 24)
        text_object.textLines(text)

        self.canvas.drawText(text_object)

    def save_pdf(self):
        self.canvas.save()

# Example usage
if __name__ == "__main__":
    title = "Sample PDF Report"
    filename = "report.pdf"
    generator = PDFReportGenerator(title, filename)

    y_position = 700
    generator.add_section("Introduction", "This is the introduction section of the report.", y_position)
    y_position -= 100
    generator.add_section("Details", "Here are more details in another section.", y_position)

    generator.save_pdf()
