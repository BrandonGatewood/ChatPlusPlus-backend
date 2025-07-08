from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.db.session import get_db
from app.exceptions import AuthorizationError, NotFoundError
from app.schemas.schema_chat import ChatResponse, ChatTitle
from app.schemas.schema_message import MessageRequest, MessageResponse
from app.schemas.user import UserId
from app.services.services_chat import create_chat_service, delete_chat_service, get_chat_service
from app.services.services_chat import get_all_chat_titles_service as get_chats_service
router = APIRouter()

@router.post("/chats/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_chat_router(
    message_request: str = Form(...),
    files_request: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: UserId = Depends(get_current_user)
) -> MessageResponse: 
    """
    Create a new chat with the user's initial message(s).
    """
    try:
        return create_chat_service(db, current_user.id, MessageRequest(text=message_request, files=files_request))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/chats/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_router(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserId = Depends(get_current_user)
) -> None:
    """
    Delete a given chat
    """
    try:
        delete_chat_service(db, chat_id, current_user.id)
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/chats", response_model=List[ChatTitle], status_code=status.HTTP_200_OK) 
def get_chats_router(
    db: Session = Depends(get_db),
    current_user: UserId = Depends(get_current_user)
) -> List[ChatTitle]:
    """
    """
    return get_chats_service(db, current_user.id)


@router.get("/chats/{chat_id}", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def get_chat_router(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserId = Depends(get_current_user)
) -> ChatResponse:
    """
    """
    try:
        return get_chat_service(db, chat_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))