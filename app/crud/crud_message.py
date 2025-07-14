import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models.message import Message
from app.db.models.chat import Chat
from app.exceptions import ChatNotFoundError, MessageNotFoundError
from app.schemas.schema_message import MessageResponse 


"""
CRUD operations for chat messages.

Includes adding new messages, editing messages, and deleting future messages
after an edit to maintain chat consistency.
"""


def add_message(
    db: Session,
    chat_id: UUID,
    sender: str,
    text: str
) -> MessageResponse:
    """
    Add a new message to the chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.
        sender: The sender of message.
        text: the sender's message text.

    Raises:
        ChatNotFoundError: If chat does not exist.

    Returns:
        The MessageResponse instance containing the id, sender, and text.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).one_or_none()
    if not chat:
        raise ChatNotFoundError(f"Chat with id {chat_id} not found.")

    message = Message(chat_id=chat_id, sender=sender, text=text)

    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageResponse.model_validate(message)


def edit_message(
    db: Session,
    message_id: UUID,
    text: str
) -> None: 
    """
    Edit the text of an existing message and delete the following messages in the given chat.

    Args:
        db: SQLAlchemy DB session.
        message_id: The unique UUID for the message.
        text: The updated message text.

    Raises:
        MessageNotFoundError: If message does not exist.

    Returns:
        None.
    """
    message = db.query(Message).filter(Message.id == message_id).one_or_none()
    if not message:
        raise MessageNotFoundError(f"Message with id {message_id} not found.")

    message.text = text

    _delete_messages_after_edit(db, message.chat_id, message.created_at)

    db.commit()


def _delete_messages_after_edit(
    db: Session,
    chat_id: UUID,
    edited_message_created_at: datetime.datetime
) -> None:
    """
    Delete all messages that were after the edited message.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.
        edited_message_created_at: The date and time when the original message was created.

    Returns:
        None.
    """
    db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.created_at > edited_message_created_at
    ).delete(synchronize_session=False)


def add_bot_message(
    db: Session,
    chat_id: UUID,
) -> MessageResponse:
    """
    adds an initial empty message from bot to the chat. 

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.
        sender: The sender of message.
        text: the sender's message text.

    Raises:
        ChatNotFoundError: If chat does not exist.

    Returns:
        The MessageResponse instance containing the id, sender, and text.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).one_or_none()
    if not chat:
        raise ChatNotFoundError(f"Chat with id {chat_id} not found.")
    
    message = Message(chat_id=chat_id, sender="bot", text="")
    
    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageResponse.model_validate(message)


def update_bot_message_text(
    db: Session,
    message: Message,
    chunk: str
) -> None:
    """
    Updates bots message to the chat. 

    Args:
        db: SQLAlchemy DB session.
        message: The bots Message instance.
        chunk: chunk of the bots message

    Raises:
        None.

    Returns:
        None.
    """
    
    message.text += chunk 

    db.commit()


def get_message(
    db: Session,
    message_id: UUID,
) -> Message:
    """
    Gets the message by id. 

    Args:
        db: SQLAlchemy DB session.
        message_id: The unique UUID for the chat.

    Raises:
        None.

    Returns:
        The Message instance.
    """
    return db.query(Message).filter(Message.id == message_id).one_or_none()
