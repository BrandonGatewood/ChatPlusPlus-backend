from typing import List
from sqlalchemy.orm import Session, joinedload
from app.db.models.chat import Chat
from app.db.models.user import User 
from app.crud.crud_message import get_messages_for_chat

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

def get_chat(db: Session, chat_id: int) -> Chat:
    chat = (
        db.query(Chat)
        .options(joinedload(Chat.messages))
        .filter(Chat.id == chat_id)
        .first()
    )

    if not chat:
        raise ValueError("Chat with id {chat_id} not found")
    return chat
    

def get_all_chat_titles(db: Session, user_id: int) -> List[tuple[id, str]]:
    chats = (
        db.query(Chat.id, Chat.title)          # select only the columns you want
        .filter(Chat.user_id == user_id)       # filter by the user's id
        .order_by(Chat.created_at.desc())      # optional: newest chats first
        .all()                                 # execute query and get list of tuples
    )
    return chats