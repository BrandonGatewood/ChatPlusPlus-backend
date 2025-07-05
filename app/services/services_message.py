from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.schemas.schema_message import MessageResponse, MessageRequest
from app.crud.crud_chat import chat_ownership
from app.crud.crud_message import add_message, edit_message
from app.exceptions import AuthorizationError, ChatNotFoundError, ExtensionsError, BotError, MessageNotFoundError, NotFoundError
from app.utils.parsers import parse_docx_bytes, parse_pdf_bytes

def add_text_message_service(
        db: Session, 
        chat_id: int, 
        user_id: int,
        msg_in: MessageRequest
    ) -> MessageResponse:
    """
    Saves a user text message and a bot response to the DB.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat's unique ID.
        user_id: The user's unique ID.
        msg_in: The user's message input.

    Raises:
        AuthorizationError: if the user is not authorized for the chat.
        ChatNotFoundError: if chat not found.

    Returns:
        MessageResponse with the bot's reply.
    """
    # Check if user owns chat 
    if not chat_ownership(db, chat_id, user_id):
        raise AuthorizationError("Not Authorized")

    # Save user's text message
    try:
        user_message = add_message(db, chat_id, "user", msg_in.text)
    except ChatNotFoundError as e:
        raise NotFoundError(f"Chat not found: {str(e)}") 

    return _get_bot_response(db, chat_id, user_message.text) 

def add_upload_message_service(
    db: Session,
    chat_id: int,
    user_id: int,
    file: UploadFile
) -> MessageResponse:
    """
    Parses an uploaded resume (PDF or DOCX), saves it as a user message,
    then adds a bot response.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat's unique ID.
        user_id: The user's unique ID.
        file: The uploaded file object.

    Raises:
        ExtensionsError: if the file type is unsupported.

    Returns:
        MessageResponse with the bot's reply.
    """
    # Parse uploaded resume into text
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ["pdf", "docx"]:
        raise ExtensionsError("Unsupported file type. Upload PDF or DOCX.")

    file_bytes = file.file.read()
    file.file.close() 

    if file_ext == "pdf":
        parsed_text = parse_pdf_bytes(file_bytes)
    else: 
        parsed_text = parse_docx_bytes(file_bytes)
    
    return add_text_message_service(db, chat_id, user_id, parsed_text)

def edit_text_message_service(
        db: Session,
        chat_id: int,
        user_id: int,
        message_id: int,
        msg_in: MessageRequest
) -> MessageResponse:
    """
    Edits an existing user message and generates a new bot response

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat's unique ID.
        user_id: The user's unique ID.
        msg_in: the users message input.

    Raises:
        AuthorizationError: if the user is not authorized for the chat.
        MessageNotFoundError: if message not found.

    Returns:
        MessageResponse with the bot's reply.
    """
    # Check if user owns chat 
    if not chat_ownership(db, chat_id, user_id):
        raise AuthorizationError("Not Authorized") 

    # Save users edited Response
    try:
        user_message = edit_message(db, message_id, msg_in.text)
    except MessageNotFoundError as e:
        raise NotFoundError(f"Message not found: {str(e)}")

    return _get_bot_response(db, chat_id, user_message.text)    

def _get_bot_response(
        db:Session, 
        chat_id:int, 
        msg_in: str 
) -> MessageResponse:
    """
    Calls the bot to generate a response to the given user message,
    saves the bot's reply, and returns it. 

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat's unique ID.
        msg_in: the users message text.

    Raises:
        BotError: if error while requesting bot's response.

    Returns:
        MessageResponse with the bot's reply.
    """
    try:
        # get bot's response with user_message
        bot_response = _call_bot(db, chat_id, msg_in)
    except BotError as e:
        raise BotError(f"Bot call failed: {str(e)}") 

    # Save bot's response 
    bot_message = add_message(db, chat_id, "bot", bot_response.text)

    return MessageResponse(text=bot_message.text) 

def _call_bot(db: Session, chat_id: int, msg_in: str) -> MessageResponse:
    return MessageResponse(text="Bot has replied to your text.")