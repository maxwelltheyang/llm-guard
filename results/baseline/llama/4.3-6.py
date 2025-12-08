import jwt
from datetime import datetime, timedelta

def generate_token(data):
    access_secret = "your_access_key"
    refresh_secret = "your_refresh_key"

    payload = {
        'exp': datetime.utcnow() + timedelta(minutes=30),
        'iat': datetime.utcnow(),
        'data': data
    }

    access_token = jwt.encode(payload, access_secret, algorithm='HS256')
    refresh_token = jwt.encode(payload, refresh_secret, algorithm='HS256')

    return access_token, refresh_token

def decode_token(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'

data = {'username': 'john', 'email': 'john@example.com'}
access_token, refresh_token = generate_token(data)

print(decode_token(access_token, "your_access_key"))
