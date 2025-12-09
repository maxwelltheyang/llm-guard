from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import requests
import contextlib

def create_pdf(packet, user_text, user_image_url):
    c = canvas.Canvas(packet)
    c.setFont("Helvetica", 12)

    if user_text:
        y = 750
        lines = user_text.split('\n')
        for line in lines:
            c.drawString(30, y, line)
            y -= 15

    if user_image_url:
        try:
            response = requests.get(user_image_url, timeout=5)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                c.drawImage(img_data, 30, y - 100, width=100, height=100)
        except requests.RequestException as e:
            print(f"An error occurred while making a request to the image URL: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    c.save()

@contextlib.contextmanager
def safe_open_file(path, mode):
    try:
        f = open(path, mode)
        yield f
    finally:
        if f:
            f.close()

def main():
    user_text = "Hello, World!"  # Example text input
    user_image_url = "https://example.com/image.jpg"  # Example image URL
    packet = BytesIO()

    try:
        create_pdf(packet, user_text, user_image_url)
        packet.seek(0)
        with safe_open_file("output.pdf", "wb") as f:
            f.write(packet.getvalue())
    except requests.RequestException as e:
        print(f"An error occurred while creating the PDF: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        packet.close()

if __name__ == "__main__":
    main()
