import requests
import os
import logging

logging.basicConfig(level=logging.INFO)

def process_payment(amount, payment_method):
    api_endpoint = "https://api.paymentprovider.com/process"
    api_key = os.getenv("PAYMENT_API_KEY")
    if api_key is None:
        logging.error("API key not found. Please set the PAYMENT_API_KEY environment variable.")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "amount": amount,
        "payment_method": payment_method
    }

    try:
        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info("Payment processed successfully.")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An error occurred: {req_err}")

    return None
