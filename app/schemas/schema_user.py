from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """
    Schema for incoming user create requests.
    """
    email: EmailStr  
    password: str    

class UserLogin(BaseModel):
    """
    Schema for incoming user login requests.
    """
    email: EmailStr
    password: str

class UserId(BaseModel):
    """
    Schema for outgoing user id.
    """
    id: UUID 