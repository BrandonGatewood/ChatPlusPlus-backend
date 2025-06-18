from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base  # Base class for all models, handles SQLAlchemy ORM setup

class User(Base):
    __tablename__ = "users"  # Name of the table in the database

    id = Column(Integer, primary_key=True, index=True)
    # Primary key column, auto-incremented integer, indexed for fast lookups

    email = Column(String, unique=True, index=True, nullable=False)
    # User's email address, must be unique, indexed for quick search, can't be null

    hashed_password = Column(String, nullable=False)
    # Hashed password string, stored securely, can't be null