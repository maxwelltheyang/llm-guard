from fpdf import FPDF

class PDFReportGenerator:
    def __init__(self, title):
        self.title = title
        self.pdf = FPDF()

    def create_pdf(self, content, filename):
        # Add a page
        self.pdf.add_page()

        # Set title
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, self.title, 0, 1, 'C')

        # Add content
        self.pdf.set_font('Arial', '', 12)
        self.pdf.multi_cell(0, 10, content)

        # Save the PDF file
        self.pdf.output(filename)

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
