from typing import List
from sqlalchemy.orm import Session, joinedload
from app.db.models.chat import Chat
from app.db.models.user import User 
from app.crud.crud_message import get_messages_for_chat
from app.exceptions import UserNotFoundError, ChatNotFoundError

"""
CRUD operations for chat .

Includes adding a new chat, getting a single chat with all messages,
getting all chat titles, deleting a single chat, and checking ownership
of a chat. 
"""

def create_chat(db: Session, user_id: int, title: str) -> Chat:
    """
    Add a new chat for the given user.

    Args:
        db: SQLAlchemy DB session.
        user_id: The user's unique ID.
        title: the title of the new chat.

    Raises:
        UserNotFoundError: if user_id does not exist.
    Returns:
        The newly created Chat instance.
    """
    with db.begin():
        user = db.query(User).filter(User.id == user_id).first()
        if not user: 
            raise UserNotFoundError(f"User with id {user_id} not found")
    
        chat = Chat(user_id=user_id, title=title)

        db.add(chat)
        db.refresh(chat)
    return chat

def delete_chat(db: Session, chat_id: int) -> None:
    """
    Delete the given chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat_id's unique ID.

    Raises:
        ChatNotFoundError: if chat_id does not exist.
    Returns:
        None.
    """
    with db.begin():
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise ChatNotFoundError(f"Chat with id {chat_id} not found")
    
        db.delete(chat)

def get_chat(db: Session, chat_id: int) -> Chat:
    """
    Get the given chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat_id's unique ID.

    Raises:
        ChatNotFoundError: if chat_id does not exist.
    Returns:
        The found Chat instance. 
    """
    with db.begin():
        chat = (
            db.query(Chat)
            .options(joinedload(Chat.messages))
            .filter(Chat.id == chat_id)
            .first()
        )

        if not chat:
            raise ChatNotFoundError(f"Chat with id {chat_id} not found")
    return chat
    
def get_all_chat_titles(db: Session, user_id: int) -> List[tuple[int, str]]:
    """
    Get the title of all chats owned by user.

    Args:
        db: SQLAlchemy DB session.
        user_id: The user_id's unique ID.

    Returns:
        The list of chat_id and title owned by user. 
    """
    with db.begin():
        chats = (
            db.query(Chat.id, Chat.title)          # select only the columns you want
            .filter(Chat.user_id == user_id)       # filter by the user's id
            .order_by(Chat.created_at.desc())      # optional: newest chats first
            .all()                                 # execute query and get list of tuples
        )
    return chats

def chat_ownership(db: Session, chat_id: int, user_id: int) -> bool:
    """
    Check if user owns the chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat_id's unique ID.
        user_id: The user_id's unique ID.

    Returns:
        True if user owns chat; False if user doesnt own chat. 
    """
    with db.begin():
        owner_id = db.query(Chat.user_id).filter(Chat.id == chat_id).scalar()

    if owner_id is None:
        return False
    
    return owner_id == user_id