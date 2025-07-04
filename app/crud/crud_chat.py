from sqlalchemy.orm import Session
from app.db.models.chat import Chat
from app.db.models.user import User 

def create_chat(db: Session, user_id: int, title: str) -> Chat:
    user = db.query.filter(User.id == user_id).first()
    if not user: 
        raise ValueError("User with id {user_id} not found")
    
    chat = Chat(user_id, title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def delete_chat(db: Session, chat_id: int) -> None:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise ValueError("Chat with id {chat_id} not found")
    
    db.delete(chat)
    db.commit()