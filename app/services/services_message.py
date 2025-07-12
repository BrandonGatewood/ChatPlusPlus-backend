from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.exceptions import AuthorizationError, NotFoundError, MessageNotFoundError, ChatNotFoundError
from app.schemas.schema_message import MessageRequest, EditMessageRequest, MessageResponse
from app.crud.crud_chat import chat_ownership
from app.crud.crud_message import edit_message
from app.services.services_shared import save_user_messages


"""
Message service functions for adding and editing messages in chats.
Handles ownership checks and bot response generation.
"""


def add_message_service(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    message_request: MessageRequest
) -> List[MessageResponse]:
    """
    Add a message and update the chat.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.
        chat_id: The unique UUID for the chat.
        message_request: The message request containing the text.

    Raises:
        AuthorizationError: If user doesnt own chat.
        NotFoundError: If ChatNotFoundError was caught.

    Returns:
        The list of MessageResponse instance containing the id, sender, and text.
    """
    try:
        if not chat_ownership(db, chat_id, user_id):
            raise AuthorizationError("Not Authorized")

        message_responses = save_user_messages(db, chat_id, message_request)

        return message_responses

    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")


def edit_text_message_service(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    message_id: UUID,
    edited_message_request: EditMessageRequest
) -> None:
    """
    Edit a message and update the chat.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.
        chat_id: The unique UUID for the chat.
        message_id: The unique UUID for the message.
        edited_message_request: The edited message request containing the new text.

    Raises: 
        AuthorizationError: If user doesnt own chat. 
        NotFoundError: If MessageNotFoundError or ChatNotFoundError was caught.

    Returns:
        None.
    """
    try:
        if not chat_ownership(db, chat_id, user_id):
            raise AuthorizationError("Not Authorized")

        edit_message(db, message_id, edited_message_request.text)

    except MessageNotFoundError as e:
        raise NotFoundError(f"Message not found: {str(e)}")
    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")
