from pydantic import BaseModel, EmailStr

# Schema for user creation (register)
class UserCreate(BaseModel):
    email: EmailStr  # validates email format
    password: str    # plain password input


# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str