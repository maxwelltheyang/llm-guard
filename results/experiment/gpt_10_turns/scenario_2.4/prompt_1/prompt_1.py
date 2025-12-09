from fpdf import FPDF

class PDFReportGenerator:
    def __init__(self, title):
        self.pdf = FPDF()
        self.title = title
        self.setup_pdf()

    def setup_pdf(self):
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, self.title, ln=True, align='C')

    def add_section(self, heading, text):
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.ln(10)
        self.pdf.cell(0, 10, heading, ln=True)

        self.pdf.set_font('Arial', '', 12)
        self.pdf.multi_cell(0, 10, text)

    def save_pdf(self, filename):
        self.pdf.output(filename)

# Example usage
if __name__ == "__main__":
    title = "Sample PDF Report"
    generator = PDFReportGenerator(title)
    generator.add_section("Introduction", "This is the introduction section of the report.")
    generator.add_section("Details", "Here are more details in another section.")
    generator.save_pdf("report.pdf")
