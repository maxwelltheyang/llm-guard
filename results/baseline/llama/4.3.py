import jwt
import datetime

secret_key = "my_secret_key"

def generate_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }

    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

# Usage example
token = generate_token(1)
print(token)

decoded_token = verify_token(token)
print(decoded_token)
