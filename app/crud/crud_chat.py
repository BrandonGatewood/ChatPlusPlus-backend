from uuid import UUID
from typing import List
from sqlalchemy.orm import Session, joinedload
from app.db.models.chat import Chat
from app.db.models.message import Message
from app.db.models.user import User 
from app.exceptions import UserNotFoundError, ChatNotFoundError
from app.schemas.schema_chat import ChatTitle

"""
CRUD operations for chat. 

Includes adding a new chat, getting a single chat with all messages,
getting all chat titles, deleting a single chat, and checking ownership
of a chat. 
"""

def create_chat(
    db: Session,
    user_id: UUID,
    title: str
) -> Chat:
    """
    Add a new chat for the given user.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.
        title: The title of the new chat.

    Raises:
        UserNotFoundError: If user does not exist.

    Returns:
        The newly created Chat instance.
    """
    user = db.query(User).filter(User.id == user_id).one_or_none()

    if user is None: 
        raise UserNotFoundError(f"User with id {user_id} not found")

    chat = Chat(user_id=user_id, title=title)

    db.add(chat)
    db.refresh(chat)

    return chat

def delete_chat(db: Session, chat_id: UUID) -> None:
    """
    Delete the given chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.

    Raises:
        ChatNotFoundError: if chat_id does not exist.

    Returns:
        None.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).one_or_none()

    if not chat:
        raise ChatNotFoundError(f"Chat with id {chat_id} not found")

    db.delete(chat)

def get_chat(db: Session, chat_id: UUID) -> Chat:
    """
    Get the given chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.

    Raises:
        ChatNotFoundError: if chat_id does not exist.

    Returns:
        The found Chat instance. 
    """
    chat = (
        db.query(Chat)
        .options(joinedload(Chat.messages))
        .filter(Chat.id == chat_id)
        .one_or_none()
    )

    if not chat:
        raise ChatNotFoundError(f"Chat with id {chat_id} not found")

    return chat
    
def get_all_chat_titles(db: Session, user_id: UUID) -> List[ChatTitle]:
    """
    Get the title of all chats owned by user.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.

    Returns:
        The list of ChatTitle objects owned by user. 
    """
    chats = (
        db.query(Chat.id, Chat.title)          # select only the columns you want
        .filter(Chat.user_id == user_id)       # filter by the user's id
        .order_by(Chat.created_at.desc())      # optional: newest chats first
        .all()                                 # execute query and get list of tuples
    )

    return [ChatTitle(id=chat_id, title=title) for chat_id, title in chats]

def get_messages_for_chat(db: Session, chat_id: UUID) -> List[Message]:
    """
    Fetch all messages belonging to a specific chat, ordered by creation time.

    Args:
        db: SQLAlchemy DB session
        chat_id: The unique UUID for the chat.

    Returns:
        List of Message objects sorted by created_at ascending
    """
    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return messages

def chat_ownership(db: Session, chat_id: UUID, user_id: UUID) -> bool:
    """
    Check if user owns the chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.
        user_id: The unique UUID for the user.

    Raises: 
        ChatNotFoundError: If chat does not exist.

    Returns:
        True if user owns chat; False if user doesnt own chat. 
    """
    owner_id = db.query(Chat.user_id).filter(Chat.id == chat_id).scalar()

    if owner_id is None:
        raise ChatNotFoundError(f"Chat with id {chat_id} not found")
    
    return owner_id == user_id