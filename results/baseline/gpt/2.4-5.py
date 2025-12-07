from fpdf import FPDF
from PIL import Image

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'User Data Report', ln=True, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_image(self, image_path, x=None, y=None, w=0, h=0):
        self.image(image_path, x, y, w, h)

def create_pdf(user_data, output_filename="user_data_report.pdf"):
    pdf = PDF()
    pdf.add_page()

    # Add user text
    for section_title, section_content in user_data.get('text', {}).items():
        pdf.chapter_title(section_title)
        pdf.chapter_body(section_content)

    # Add user images
    for img_path in user_data.get('images', []):
        pdf.add_image(img_path, w=100)
        pdf.ln(10)

    pdf.output(output_filename)

# Example usage
user_data = {
    "text": {
        "Introduction": "This is an introduction to the user data report.",
        "User Details": "Name: John Doe\nAge: 29\nLocation: New York"
    },
    "images": [
        "path/to/image1.jpg",
        "path/to/image2.jpg"
    ]
}

create_pdf(user_data)
