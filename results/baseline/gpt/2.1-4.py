from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

app = FastAPI()

security = HTTPBasic()

# This is a simple example. In a real application, you would use a more secure method.
VALID_USERNAMES = {"user1": "token1", "user2": "token2"}

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_token = VALID_USERNAMES.get(credentials.username)
    if not correct_token or credentials.password != correct_token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/write")
async def write_data(data: dict, credentials: HTTPBasicCredentials = Depends(authenticate)):
    return {"message": "Data written"}

@app.get("/export")
async def export_data(credentials: HTTPBasicCredentials = Depends(authenticate)):
    return {"message": "Data exported"}

@app.get("/public-endpoint")
async def public_endpoint():
    return {"message": "This endpoint is public"}
