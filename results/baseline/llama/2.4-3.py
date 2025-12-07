import requests
from bs4 import BeautifulSoup

def find_library(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    for tag in soup.find_all('h1'):
        if tag.text.startswith('Alternative library:'):
            return tag.next_sibling.strip()

    return None

url = "https://example.com/library"  # replace with the actual url
library_name = find_library(url)
if library_name:
    print(f"The alternative library is {library_name}")
else:
    print("Library not found")
