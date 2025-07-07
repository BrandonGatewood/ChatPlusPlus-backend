from uuid import UUID
from sqlalchemy.orm import Session
from app.exceptions import AuthorizationError, NotFoundError, MessageNotFoundError, ChatNotFoundError
from app.schemas.schema_message import MessageRequest, EditMessageRequest, MessageResponse
from app.crud.crud_chat import chat_ownership
from app.crud.crud_message import add_message, edit_message
from app.services.services_shared import save_user_messages, build_prompt, call_bot


"""
Message service functions for adding and editing messages in chats.
Handles ownership checks and bot response generation.
"""


def add_message_service(
    db: Session,
    chat_id: UUID,
    user_id: UUID,
    msg_in: MessageRequest
) -> MessageResponse:
    """
    Add message(s) to a given chat.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat_id's unique ID.
        user_id: The user_id's unique ID.
        msg_in: The user's message request.
    Raises: 
        AuthorizationError: if user doesnt own chat. 
        NotFoundError: if ChatNotFoundError was caught.

    Returns:
        The MessageResponse object from the bot.
    """
    if not chat_ownership(db, chat_id, user_id):
        raise AuthorizationError("Not Authorized")

    try:
        with db.begin():
            save_user_messages(db, chat_id, msg_in)

            prompt = build_prompt(db, chat_id)
            bot_response = call_bot(prompt)

            add_message(db, chat_id, "bot", bot_response.text)

        return bot_response

    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")


def edit_text_message_service(
    db: Session,
    user_id: UUID,
    chat_id: UUID,
    message_id: UUID,
    edited_message_request: EditMessageRequest
) -> MessageResponse:
    """
    Edit a message and update the chat with a new bot response.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.
        chat_id: The unique UUID for the chat.
        message_id: The unique UUID for the message.
        edited_message_request: The edited message request containing the new text.

    Raises: 
        AuthorizationError: If user doesnt own chat. 
        NotFoundError: If ChatNotFoundError was caught.

    Returns:
        The message response object with the bot's response.
    """
    if not chat_ownership(db, chat_id, user_id):
        raise AuthorizationError("Not Authorized")

    try:
        with db.begin():
            edit_message(db, message_id, edited_message_request.text)

            prompt = build_prompt(db, chat_id)
            bot_response = call_bot(prompt)

            add_message(db, chat_id, "bot", bot_response.text)

        return bot_response

    except MessageNotFoundError as e:
        raise NotFoundError(f"Message not found: {str(e)}")
    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")