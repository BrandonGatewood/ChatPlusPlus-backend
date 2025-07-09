from typing import Optional
from uuid import UUID
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import MultipleResultsFound
from app.db.models.user import User
from app.core.security import hash_password


"""
CRUD operations for authentication.

Includes creating a new user, finding an existing user, 
and checking existing email.
"""


def create_user(
    db: Session,
    user_request_email: EmailStr,
    user_request_password: str
) -> UUID:
    """
    Add a new user.

    Args:
        db: SQLAlchemy DB session.
        user_request_email: The unique email for the new user.
        user_reuest_password: The password for the new user.

    Returns:
        The UUID for the user.
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
    Find an existing user.

    Args:
        db: SQLAlchemy DB session.
        user_request_email: The unique email for the user.

    Raises:
        RunTimeError: If more than 1 user has the same email.

    Returns:
        The User instance or None.
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
    Check if the email already exists.

    Args:
        db: SQLAlchemy DB session.
        email: The unique email for the user.

    Returns:
        True if email exists; False if email doesnt exist.
    """
    return db.query(
        db.query(User).filter(User.email == email).exists()
    ).scalar() 