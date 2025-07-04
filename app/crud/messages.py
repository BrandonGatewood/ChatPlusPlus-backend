from sqlalchemy.orm import Session
from app.db.models.message import Message
from app.db.models.chat import Chat

def add_message(db: Session, chat_id: int, sender: str, text: str) -> Message:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise ValueError(f"Chat with id {chat_id} not found")

    message = Message(chat_id=chat_id, sender=sender, text=text)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_messages_for_chat(db: Session, chat_id: int) -> list[Message]:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise ValueError(f"Chat with id {chat_id} not found")

    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()