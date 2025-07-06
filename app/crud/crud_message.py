import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models.message import Message
from app.db.models.chat import Chat
from app.exceptions import ChatNotFoundError, MessageNotFoundError 

"""
CRUD operations for chat messages.

Includes adding new messages, editing messages, and deleting future messages
after an edit to maintain chat consistency.
"""

def add_message(db: Session, chat_id: UUID, sender: str, text: str) -> None:
    """
    Add a new message to the given chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat's unique ID.
        sender: sender of message.
        text: the sender's message text.

    Raises:
        ChatNotFoundError: if chat_id does not exist.

    Returns:
        None.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).one_or_none()
    if not chat:
        raise ChatNotFoundError(f"Chat with id {chat_id} not found")

    message = Message(chat_id=chat_id, sender=sender, text=text)

    db.add(message)
    db.refresh(message)

def edit_message(db: Session, message_id: UUID, text: str) -> None: 
    """
    Edit the text of an existing message and delete the following messages in the given chat.

    Args:
        db: SQLAlchemy DB session.
        message_id: The message's unique ID.
        text: the updated message text.

    Raises:
        MessageNotFoundError: if message_id does not exist.

    Returns:
        None.
    """
    message = db.query(Message).filter(Message.id == message_id).one_or_none()
    if not message:
        raise MessageNotFoundError(f"Message with id {message_id} not found")

    message.text = text

    _delete_messages_after_edit(db, message.chat_id, message.created_at)

def _delete_messages_after_edit(db: Session, chat_id: UUID, edited_message_created_at: datetime.datetime) -> None:
    """
    Deletes all messages that were after the edited message.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat's unique ID.
        edited_message_created_at: the date and time when the original message was created.

    Returns:
        None.
    """
    db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.created_at > edited_message_created_at
    ).delete(synchronize_session=False)