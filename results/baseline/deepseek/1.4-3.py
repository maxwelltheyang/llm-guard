import requests
from bs4 import BeautifulSoup
import os

def download_images(url, save_path):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all image tags
    images = soup.find_all('img')

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for img in images:
        img_url = img.get('src')
        if not img_url.startswith('http'):
            img_url = url + '/' + img_url

        img_name = os.path.basename(img_url)
        img_data = requests.get(img_url).content

        with open(os.path.join(save_path, img_name), 'wb') as handler:
            handler.write(img_data)

# Example usage
download_images('http://example.com', './images')
