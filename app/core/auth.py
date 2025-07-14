import json
import uuid
from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.schema_user import UserId
from app.core.jwt import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserId:
    """
    extract the user's id from the Jason Web Token in a standard HTTP request.

    Args:
        token: The Jason Web Token.
        db: SQLAlchemy DB session.

    Raises:
        HTTPException: If Jason Web Token is invalid.
    
    Returns:
        The UserId instance containing id UUID.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        print("Decoded sub:", user_id_str)

        if user_id_str is None:
            raise credentials_exception

        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError, TypeError) as e:
        print("Error decoding token or converting UUID:", e)
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return UserId(id=user_id) 



async def get_current_user_ws(
    websocket: WebSocket,
    db: Session = Depends(get_db)
) -> UserId:
    """
    extract the user's id from the Jason Web Token sent over a WebSocket connection.

    Args:
        websocket: The Websocket.
        db: SQLAlchemy DB session.

    Raises:
        .Close: If Jason Web Token is invalid or user not found.
    
    Returns:
        The UserId instance containing id UUID.
    """
    msg = await websocket.receive_text()
    data = json.loads(msg)
    if data.get("type") != "access_token" not in data:
        await websocket.close(code=1008, reason="Unauthorized: No token")
        return
    
    token = data["access_token"]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            await websocket.close(code=1008, reason="Unauthorized: no user id str")
            return None
        user_id = uuid.UUID(user_id_str)
    except Exception:
        await websocket.close(code=1008, reason="Unauthorized: cant decode jwt")
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1008, reason="Unaothorized: User not found")
        return None

    return UserId(id=user_id)