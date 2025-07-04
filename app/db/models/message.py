from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, relationship;
from app.db.models.base import Base  # Base class for all models, handles SQLAlchemy ORM setup

class Message(Base):
    __tablename__ = "messages"  # Name of the table in the database

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("Chat", back_populates="messages")