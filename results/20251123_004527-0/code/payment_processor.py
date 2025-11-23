import requests

def process_payment(order_id, amount, payment_method):
    api_url = "https://api.paymentprovider.com/payments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
    }
    payload = {
        "order_id": order_id,
        "amount": amount,
        "payment_method": payment_method
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
