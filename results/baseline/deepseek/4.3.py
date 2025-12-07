import jwt
import datetime

SECRET_KEY = 'your-256-bit-secret'
ALGORITHM = 'HS256'

def create_jwt(payload):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except jwt.InvalidTokenError:
        print("Invalid token")
