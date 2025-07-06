import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.db.models.base import Base  # Base class for all models, handles SQLAlchemy ORM setup

"""
SQLAlchemy Chat model definition, representing a chat with messages.
"""

class Chat(Base):
    __tablename__ = "chats"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", passive_deletes=True, order_by="Message.created_at.asc()")