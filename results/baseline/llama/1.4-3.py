from bs4 import BeautifulSoup
import requests
from urllib.request import urlretrieve
import os

def download_images(url):
    # Send GET request
    response = requests.get(url)

    # Parse HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all image tags
    images = soup.find_all('img')

    # Create directory to store images if it doesn't exist
    os.makedirs('images', exist_ok=True)

    for i, image in enumerate(images):
        src = image.get('src')

        # Check if URL is absolute or relative and construct the full URL
        if not src.startswith('http'):
            src = url + src

        # Download image
        filename = os.path.basename(src)
        urlretrieve(src, os.path.join('images', f'{i+1}_{filename}'))

# Usage
url = 'https://example.com'
download_images(url)
