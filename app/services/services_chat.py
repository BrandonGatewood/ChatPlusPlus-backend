from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.exceptions import AuthorizationError, UserNotFoundError, NotFoundError, ChatNotFoundError
from app.schemas.schema_chat import ChatResponse, ChatTitle
from app.schemas.schema_message import MessageRequest
from app.crud.crud_chat import chat_ownership, create_chat, delete_chat, get_all_chat_titles, get_chat
from app.services.services_shared import save_user_messages


"""
Chat service functions for creating, retrieving, listing, and deleting chats.
Handles ownership checks and coordinates chat-related database operations.
"""


def create_chat_service(
    db: Session,
    user_id: UUID,
    message_request: MessageRequest
) -> ChatTitle:
    """
    Create a new chat with the user's initial message(s).

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.
        message_request: The message request containing the text.

    Raises: 
        NotFoundError: If UserNotFoundError or ChatNotFoundError was caught.

    Returns:
        The ChatTitle instance containing the new id and title.
    """
    try:
        # NEED TO CALL LLM TO GENERATE TITLE!!
        # title = generateTitile(message_request)
        chatTitle = create_chat(db, user_id, "Chat Title")
        message_reposonses = save_user_messages(db, chatTitle.id, message_request)

        return chatTitle

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
    try:
        if not chat_ownership(db, chat_id, user_id):
            raise AuthorizationError("Not Authorized")

        delete_chat(db, chat_id)

    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")


def get_chat_service(
    db: Session,
    chat_id: UUID,
    user_id: UUID
) -> ChatResponse:
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
        The ChatResponse instance containg all metadata of found chat.
    """
    try:
        if not chat_ownership(db, chat_id, user_id):
            raise AuthorizationError("Not Authorized")

        chat = get_chat(db, chat_id)

        return ChatResponse.model_validate(chat) 

    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}")


def get_all_chat_titles_service(
    db: Session,
    user_id: UUID
) -> List[ChatTitle]:
    """
    Get all the chats owned by user.

    Args:
        db: SQLAlchemy DB session.
        user_id: The unique UUID for the user.

    Returns:
        The list of ChatTitle instance containing the id and title.
    """
    chats = get_all_chat_titles(db, user_id)

    return chats
