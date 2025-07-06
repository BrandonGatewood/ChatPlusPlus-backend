import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, Index
from sqlalchemy.orm import relationship
from app.db.models.base import Base  # Base class for all models, handles SQLAlchemy ORM setup

"""
SQLAlchemy Message model definition, representing messages in chats.
"""

class Message(Base):
    __tablename__ = "messages"  # Name of the table in the database

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    chat = relationship("Chat", back_populates="messages")

    __table_args__ = (
        Index("ix_message_chat_id_created_at", "chat_id", "created_at"),
    )