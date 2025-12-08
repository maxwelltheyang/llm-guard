from fpdf import FPDF

class PDFReport:
    def __init__(self):
        self.pdf = FPDF()

    def add_page(self):
        self.pdf.add_page()

    def cell(self, width, height, txt, ln=True):
        self.pdf.cell(width=width, h=height, txt=txt, ln=ln)

    def image(self, file, w=0, h=0):
        self.pdf.image(file, w=w, h=h)

    def output(self, filename):
        self.pdf.output(filename)

# Example usage:
report = PDFReport()
report.add_page()
report.cell(100, 10, 'Hello World!', ln=True)
report.image('logo.png', w=50, h=20)
report.output('example.pdf')
