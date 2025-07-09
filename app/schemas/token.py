from pydantic import BaseModel;

class Token(BaseModel):
    """
    Schema for JWT.
    """
    access_token: str