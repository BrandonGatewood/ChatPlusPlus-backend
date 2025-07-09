from sqlalchemy.orm import Session
from app.core.jwt import create_access_token
from app.core.security import verify_password
from app.crud.crud_auth import check_email, create_user, find_user
from app.exceptions import AuthorizationError, ValidationError
from app.schemas.schema_user import UserCreate, UserLogin
from app.schemas.token import Token


def login_service(
    db: Session,
    user_request: UserLogin
) -> Token:
    """
    """
    user = find_user(db, user_request.email)

    if not user or not verify_password(user_request.password, user.hashed_password):
        raise AuthorizationError("Invalid email or password.")

    return Token(access_token=create_access_token({"sub": str(user.id)}))

def register_service(
        db: Session,
        user_request: UserCreate
) -> Token:
    """
    """
    if check_email(db, user_request.email):
        raise ValidationError("Email already in use.")
    
    user_id = create_user(db, user_request.email, user_request.password)

    return Token(access_token=create_access_token({"sub": str(user_id)}))