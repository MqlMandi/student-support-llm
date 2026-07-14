from fastapi import Header, HTTPException
from backend.config import SECRET_ACCESS_CODE

def verify_token(x_access_token: str = Header(None)):
    if x_access_token != SECRET_ACCESS_CODE:
        raise HTTPException(status_code=401, detail="Invalid Access Code.")
