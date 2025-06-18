from sqlalchemy.ext.declarative import declarative_base

# This creates a base class that our ORM models will inherit from.
# It sets up the SQLAlchemy declarative system.
Base = declarative_base()