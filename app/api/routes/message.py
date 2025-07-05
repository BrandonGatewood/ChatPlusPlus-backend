from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.session import get_db
from app.services.services_message import add_text_message_service, add_upload_message_service, edit_text_message_service
from app.schemas.schema_message import MessageRequest, MessageResponse
from app.schemas.user import UserId
from app.exceptions import AuthorizationError, ExtensionsError, BotError, NotFoundError

router = APIRouter()

@router.post("/{chat_id}/messages", response_model=MessageResponse)
def add_text_message(
    chat_id: int,
    msg_in: MessageRequest,
    db: Session = Depends(get_db),
    current_user: UserId  = Depends(get_current_user),
) -> MessageResponse:
    """
    Add a user message, generate a bot response and save both messages.

    Raises:
        HTTPException: if AuthorizationError, ChatNotFoundError, or BotError was caught.
    Returns: 
        MessageResponse with the bot's response.
    """
    try:
        return add_text_message_service(db, chat_id, current_user.id, msg_in)
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BotError as e:
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/{chat_id}/upload", response_model=MessageResponse)
def add_upload_message(
    chat_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserId = Depends(get_current_user),
) -> MessageResponse:
    """
    Parses users pdf/docx document, generate a bot response and saves both.

    Raises:
        HTTPException: if ExtensionsError, AuthorizationError, ChatNotFoundError, or BotError was caught.
    Returns:
        MessageResponse with the bot's response.
    """

    try:
        return add_upload_message_service(db, chat_id, current_user.id, file)
    except ExtensionsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BotError as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
@router.post("/{chat_id}/{message_id}", response_model=MessageResponse)
def edit_text_message(
    chat_id: int,
    message_id: int,
    msg_in: MessageRequest,
    db: Session = Depends(get_db),
    current_user: UserId = Depends(get_current_user),
) -> MessageResponse: 
    """
    Edit an existing user message, generate a new bot response, and save both.

    Raises:
        HTTPException: if AuthorizationError or BotError is caught.
    Returns:
        MessageResponse with the bot's response.
    """ 
    try:
        return edit_text_message_service(db, chat_id, current_user.id, message_id, msg_in)
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BotError as e:
        raise HTTPException(status_code=500, detail=str(e)) 