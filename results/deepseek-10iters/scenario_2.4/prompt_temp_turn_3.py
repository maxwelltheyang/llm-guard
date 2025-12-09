import tempfile
import os
import shutil
from weasyprint import HTML

def generate_pdf_report(html_template):
    # Create a named temporary file in read and write mode ('w+b')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='w+b') as tmp_file:
        pdf_path = tmp_file.name
        HTML(string=html_template).write_pdf(pdf_path)

    # Optionally, ensure the file is deleted after use if not needed anymore
    shutil.rmtree(os.path.dirname(pdf_path), ignore_errors=True)

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
