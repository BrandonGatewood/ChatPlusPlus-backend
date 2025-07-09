from typing import Optional
from uuid import UUID
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import MultipleResultsFound
from app.db.models.user import User
from app.core.security import hash_password

"""
CRUD operations for authentication.


"""
def create_user(
    db: Session,
    user_request_email: EmailStr,
    user_request_password: str
) -> UUID:
    """
    """
    hashed_pwd = hash_password(user_request_password)
    new_user = User(email=user_request_email, hashed_password=hashed_pwd)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user.id


def find_user(
    db: Session,
    user_request_email: EmailStr 
) -> Optional[User]:
    """
    """
    try:
        return db.query(User).filter(User.email == user_request_email).one_or_none()
    except MultipleResultsFound:
        # Log or raise a custom exception — this shouldn't happen if email is unique
        raise RuntimeError(f"Multiple users found with the same email: {user_request_email}")


def check_email(
    db: Session,
    email: EmailStr 
) -> bool:
    """
    """
    return db.query(
        db.query(User).filter(User.email == email).exists()
    ).scalar() 

