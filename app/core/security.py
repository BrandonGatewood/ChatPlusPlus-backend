from passlib.context import CryptContext

# Setup password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash the user's password.

    Args:
        password: the user's password.
    
    Returns:
        The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password with the hashed password.

    Args:
        plain_password: password entered that needs to be verified.
        hashed_password: saved password.

    Returns:
        True if passwords match; False if  passwords dont match.
    """
    return pwd_context.verify(plain_password, hashed_password)