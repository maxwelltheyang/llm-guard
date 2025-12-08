import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_images(url, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    img_tags = soup.find_all('img')

    for img in img_tags:
        img_url = img.get('src')
        if not img_url:
            continue
        img_url = urljoin(url, img_url)
        img_name = os.path.basename(img_url)
        img_path = os.path.join(download_folder, img_name)

        img_data = requests.get(img_url).content
        with open(img_path, 'wb') as f:
            f.write(img_data)

# Example usage:
# download_images('https://example.com', 'downloaded_images')
