from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, HTTPException, status, Form, UploadFile
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.session import get_db
from app.services.services_message import add_message_service, edit_text_message_service
from app.schemas.schema_message import EditMessageRequest, MessageRequest, MessageResponse
from app.schemas.user import UserId
from app.exceptions import AuthorizationError, ExtensionsError, BotError, NotFoundError

router = APIRouter()

@router.post("/chats/{chat_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message_router(
    chat_id: UUID,
    message_request: str = Form(...),
    files_request: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: UserId  = Depends(get_current_user),
) -> MessageResponse:
    """
    Add a message and update the chat with a new bot response.

    Args:
        chat_id: The unique UUID for the chat.
        message_request: The message request containing the text.
        db: SQLAlchemy DB session.
        current_user: The current authenticated user.

    Raises:
        HTTPException: If AuthorizationError or NotFoundError was caught.

    Returns:
        The message response with the bot's response.
    """
    try:
        return add_message_service(db, current_user.id, chat_id, MessageRequest(text=message_request, files=files_request))
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    
@router.post("/chats/{chat_id}/{message_id}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def edit_text_message_router(
    chat_id: UUID,
    message_id: UUID,
    edited_message_request: EditMessageRequest,
    db: Session = Depends(get_db),
    current_user: UserId = Depends(get_current_user),
) -> MessageResponse: 
    """
    Edit a message and update the chat with a new bot response.

    Args:
        chat_id: The unique UUID for the chat.
        message_id: The unique UUID for the message.
        edited_message_request: The edited message request containing the new text.
        db: SQLAlchemy DB session.
        current_user: The current authenticated user.

    Raises:
        HTTPException: If AuthorizationError was caught.

    Returns:
        The message response with the bot's response.
    """ 
    try:
        return edit_text_message_service(db, current_user.id, chat_id, message_id, edited_message_request)
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))