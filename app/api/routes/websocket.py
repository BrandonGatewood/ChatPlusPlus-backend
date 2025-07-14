import uuid
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.crud.crud_chat import chat_ownership
from app.core.auth import get_current_user_ws
from app.db.session import get_db
from app.services.services_websocket import build_prompt_service, stream_bot_response_service

router = APIRouter()

@router.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
) -> None:
    """
    Endpoint for streaming bot response.

    Args:
        websocket: The websocket connection.
        db: The SQLAlchemy DB session.
    
    Closes:
        Code=1008: Invalid chat id query.
        Code=1008: Invalid chat id.
        Code=1008: Invalid message id query.
        Code=1008: Invalid message id.

    Returns:
        None.
    """
    try:
        await websocket.accept()

        # Get and validate chat_id
        chat_id_str = websocket.query_params.get("chat_id")
        if not chat_id_str:
            await websocket.close(code=1008, reason="Invalid chat id query.")
            return
        try:
            chat_id = uuid.UUID(chat_id_str)
        except ValueError:
            await websocket.close(code=1008, reason="Invalid chat id.")
            return
        
        message_id_str = websocket.query_params.get("message_id")
        if not message_id_str:
            await websocket.close(code=1008, reason="Invalid message id query.")  # Policy Violation
            return
        try:
            message_id = uuid.UUID(message_id_str)
        except ValueError:
            await websocket.close(code=1008, reason="Invalid message id.")
            return



        user_id = await get_current_user_ws(websocket, db)

        if not chat_ownership(db, chat_id, user_id):
            await websocket.close(code=1008, reason="Not Authorized.")
            return

        prompt = build_prompt_service(db, user_id.id, chat_id)
        await stream_bot_response_service(websocket, db, chat_id, message_id, prompt)

    except WebSocketDisconnect:
        print("Client disconnected") 
    