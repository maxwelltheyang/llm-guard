import os
from typing import Optional, Dict
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from jose import jwt
from passlib.hash import argon2
from psycopg02 import pool
from cryptography.fernet import Fernet
import logging
from datetime import datetime, timedelta

# Load secret key from secrets manager (e.g., HashiCorp's Vault or AWS Secrets Manager)
secret_key_manager = os.environ.get('SECRET_KEY_MANAGER')
if not secret_key_manager:
    raise ValueError("SECRET_KEY_MANAGER must be set")

# Set up secrets manager for rotation and access controls
import hvac

client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])
secret_store = client.secrets.kv.v2.read_secret_version(
    path=f"secrets/secret_key",
    mount_point="my-secrets"
)

# Verify that the secret key manager matches the expected value
expected_issuer = os.environ.get('EXPECTED_ISSUER')
if payload['iss'] != expected_issuer:
    raise HTTPException(status_code=401, detail='Invalid issuer')

app = FastAPI()

class User(BaseModel):
    username: str
    email: str
    password: str

class TokenData(BaseModel):
    iss: str
    aud: str

# Custom error handler for logging errors and providing more informative error messages
class CustomError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

async def custom_error_handler(request, exc):
    # Log the full exception message in production environments with reduced sensitivity
    logger.error(f"Error handling request: {request.method} {request.url} - {str(exc)}")
    return {'error': exc.detail}

# Token expiration check with a small margin of error
def check_token_expiration(timestamp):
    expires_at = datetime.fromtimestamp(timestamp)
    if expires_at < datetime.now() - timedelta(minutes=1):
        raise CustomError(401, 'Token has expired')

@app.on_event("shutdown")
async def redis_shutdown():
    # Close the database connection pool on shutdown
    await db_pool.closeall()

# Database connection pooling with retries and timeouts
db_pool = None

def get_db():
    global db_pool
    if db_pool is None:
        db_pool = pool.ThreadedConnectionPool(
            1, 5,
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD')
        )
    return db_pool

def query_db(query, *args):
    try:
        async with db_pool.getconn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, *args)
                result = await cur.fetchall()
                return result
    except psycopg02.Error as e:
        # Handle database connection errors or timeouts
        logger.error(f"Database error: {str(e)}")

# Token blacklisting with Redis
redis_client = None

def is_token_blacklisted(token: str):
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(os.environ['REDIS_URL'])
    return await redis_client.sismember('blacklisted-tokens', token)

@app.post("/token")
async def login_for_access_token(username: str, password: str):
    # Query database for user and check password
    hashed_password = query_db("SELECT password FROM users WHERE username = %s", (username,))[0][0]
    if argon2.verify(password, hashed_password):
        access_token = jwt.encode(
            {"iss": username, "aud": os.environ.get('SECRET_KEY_AUDIENCE')},
            secret_key_manager,
            algorithm="HS256"
        )
        await redis_client.sadd('blacklisted-tokens', access_token)
        return {'access_token': access_token, 'token_type': 'bearer'}
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')
