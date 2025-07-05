import datetime
from sqlalchemy.orm import Session
from app.db.models.message import Message
from app.db.models.chat import Chat

"""
CRUD operations for chat messages.

Includes adding new messages, editing messages, and deleting future messages
after an edit to maintain chat consistency.
"""

def add_message(db: Session, chat_id: int, sender: str, text: str) -> Message:
    """
    Add a new message to the given chat.

    Raises:
        ValueError: if chat_id does not exist.
    Returns:
        The newly created Message instance.
    """
    with db.begin():
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise ValueError(f"Chat with id {chat_id} not found")

        message = Message(chat_id=chat_id, sender=sender, text=text)

        db.add(message)
        db.refresh(message)
    return message

def edit_message(db: Session, message_id: int, text: str) -> Message: 
    """
    Edit the text of an existing message and delete the following messages in the given chat.

    Raises:
        ValueError: if message_id does not exist.
    Returns:
        The updated Message instance.
    """

    with db.begin():
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            raise ValueError(f"Message with id {message_id} not found")

        message.text = text

        _delete_messages_after_edit(db, message.chat_id, message.created_at)
        db.refresh(message) 
    return message

def _delete_messages_after_edit(db: Session, chat_id: int, edited_message_created_at: datetime.datetime) -> None:
    db.query(Message).filter(
        Message.chat_id == chat_id,
        Message.created_at > edited_message_created_at
    ).delete(synchronize_session=False)