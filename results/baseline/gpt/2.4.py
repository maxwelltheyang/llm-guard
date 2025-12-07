from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'User Data Report', ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_user_data(self, user_text, image_path):
        self.add_page()

        # Add user text
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, user_text)
        self.ln(10)

        # Add image
        if image_path:
            self.image(image_path, x=10, y=self.get_y(), w=100)
            self.ln(10)

def create_user_report(user_text, image_path, filename):
    pdf = PDFReport()
    pdf.add_user_data(user_text, image_path)
    pdf.output(filename)

# Example usage:
user_text = "This is some user provided text for the report."
image_path = "path/to/user_image.png"
output_filename = "user_report.pdf"

create_user_report(user_text, image_path, output_filename)
