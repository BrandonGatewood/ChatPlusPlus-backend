from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt  # PyJWT library
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

# Replace with your secret key; keep it safe!
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict) -> str:
    """
    Create a signed JWT encoding user id and expiration date.

    Args:
        data: A dictionary containing the user data to include in the token payload (e.g., {"sub": user_id}).

    Returns:
        A signed JWT as a Base64-encoded string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT, ensuring it is valid and not expired.

    Args:
        token: The JWT string to verify.

    Raises:
        HTTPException: If the token has expired or is otherwise invalid, raises a 401 Unauthorized error.

    Returns:
        The decoded token payload containing the claims.
    """ 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")