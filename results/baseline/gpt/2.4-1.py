from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Title of the Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)

    for item in data:
        pdf.cell(0, 10, item, 0, 1)

    pdf.output('report.pdf')

data = ['Line 1', 'Line 2', 'Line 3']
generate_pdf(data)
