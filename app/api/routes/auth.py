from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.exceptions import AuthorizationError, ValidationError
from app.schemas.schema_user import UserCreate, UserLogin 
from app.schemas.token import Token
from app.services.services_auth import login_service, register_service

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    user_request: UserCreate, 
    db: Session = Depends(get_db)
) -> Token:
    """
    Register a user to the db. 

    Args:
        message_request: The user request containing email and password.
        db: SQLAlchemy DB session.

    Raises: 
        HTTPException: If ValidationError was caught.

    Returns:
        The Jason Web Token. 
    """
    try:
        return register_service(db, user_request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) 


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(
    user_request: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Log an existing user in. 

    Args:
        user_request: The user request containing email and password.
        db: SQLAlchemy DB session.

    Raises: 
        HTTPException: If AuthorizationError was caught.

    Returns:
        The Jason Web Token. 
    """
    try:
        return login_service(db, user_request)
    except AuthorizationError as e:
        raise HTTPException(status_code=401, details=str(e))