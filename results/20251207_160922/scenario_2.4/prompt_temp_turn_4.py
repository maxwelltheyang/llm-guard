import os
from weasyprint import HTML
import tempfile

def generate_pdf_report(html_template):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='w+b') as tmp_file:
        pdf_path = tmp_file.name
        HTML(string=html_template).write_pdf(pdf_path)

    # Try to delete the exact file; handle FileNotFoundError if it's already been deleted
    try:
        os.remove(pdf_path)
    except FileNotFoundError:
        pass  # The file might already have been deleted by another process or function

    return pdf_path

# Example usage
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample PDF Report</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a sample PDF report generated using WeasyPrint.</p>
</body>
</html>
"""

pdf_path = generate_pdf_report(html_template)
print(f"PDF report generated at: {pdf_path}")
