from pydantic import BaseModel, EmailStr

# Schema for user creation (register)
class UserCreate(BaseModel):
    email: EmailStr  # validates email format
    password: str    # plain password input

# Schema for user response (what we send back to client)
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True  # tells Pydantic to read data from ORM objects

# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str