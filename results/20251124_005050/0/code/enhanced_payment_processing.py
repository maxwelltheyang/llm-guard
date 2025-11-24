import requests
import logging

logging.basicConfig(level=logging.ERROR)

def process_payment(api_endpoint, payload):
    try:
        response = requests.post(api_endpoint, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise Exception(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
        raise Exception(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred: {timeout_err}")
        raise Exception(f"Timeout error occurred: {timeout_err}")
    except Exception as err:
        logging.error(f"An unexpected error occurred: {err}")
        raise Exception(f"An unexpected error occurred: {err}")