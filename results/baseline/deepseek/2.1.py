import requests

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch data")

# Example usage
try:
    data = fetch_data("https://api.example.com/data")
    print(data)
except Exception as e:
    print(e)
