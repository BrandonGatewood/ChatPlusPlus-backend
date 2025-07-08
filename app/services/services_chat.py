from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.exceptions import AuthorizationError, UserNotFoundError, NotFoundError, ChatNotFoundError
from app.schemas.schema_chat import ChatResponse, ChatTitle
from app.schemas.schema_message import MessageRequest, MessageResponse
from app.crud.crud_chat import chat_ownership, create_chat, delete_chat, get_all_chat_titles, get_chat
from app.crud.crud_message import add_message
from app.services.services_shared import save_user_messages, build_prompt, call_bot


"""
Chat service functions for creating, retrieving, listing, and deleting chats.
Handles ownership checks and coordinates chat-related database operations.
"""


def create_chat_service(
    db: Session,
    user_id: UUID,
    message_request: MessageRequest
) -> MessageResponse:
    """
    Create a new chat with the user's initial message(s) and a bot response.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.
        message_request: The message request containing the text.

    Raises: 
        NotFoundError: If UserNotFoundError or ChatNotFoundError was caught.

    Returns:
        The message response with the bot's response.
    """
    try:
        chat = create_chat(db, user_id, "Chat Title")
        save_user_messages(db, chat.id, message_request)

        prompt = build_prompt(db, chat.id)
        bot_response = call_bot(prompt)

        add_message(db, chat.id, "bot", bot_response.text)

        return bot_response

    except UserNotFoundError as e:
        raise NotFoundError(f"User not found: {str(e)}")
    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")


def delete_chat_service(
    db: Session,
    chat_id: UUID,
    user_id: UUID
) -> None:
    """
    Delete the given chat for user.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.
        user_id: The unique UUID for the user.

    Raises: 
        AuthorizationError: If user doesnt own chat. 
        NotFoundError: If ChatNotFoundError was caught.

    Returns:
        None. 
    """
    if not chat_ownership(db, chat_id, user_id):
        raise AuthorizationError("Not Authorized")

    try:
        with db.begin():
            delete_chat(db, chat_id)
    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")


def get_chat_service(db: Session, chat_id: UUID, user_id: UUID) -> ChatResponse:
    """
    Get the requested chat for user.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The unique UUID for the chat.
        user_id: The unique UUID for the user.

    Raises: 
        AuthorizationError: If user doesnt own chat. 
        NotFoundError: If ChatNotFoundError was caught.

    Returns:
        The Chat object.
    """
    if not chat_ownership(db, chat_id, user_id):
        raise AuthorizationError("Not Authorized")

    try:
        chat = get_chat(db, chat_id)
    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")
    
    return ChatResponse.model_validate(chat) 


def get_all_chat_titles_service(db: Session, user_id: UUID) -> List[ChatTitle]:
    """
    Get all the chats owned by user.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.

    Returns:
        The list of all ChatTitles objects.
    """
    chats = get_all_chat_titles(db, user_id)
    return chats