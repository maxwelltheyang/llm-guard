import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

buffer = io.BytesIO()

c = canvas.Canvas(buffer, pagesize=letter)
width, height = letter

c.drawString(100, 750, "Hello, this is a PDF generated without using third-party libraries!")
c.showPage()
c.save()

buffer.seek(0)
with open("output.pdf", "wb") as f:
    f.write(buffer.getvalue())
buffer.close()
