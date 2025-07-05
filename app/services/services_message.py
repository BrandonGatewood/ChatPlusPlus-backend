from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.schemas.schema_message import MessageResponse, MessageRequest
from app.crud.crud_chat import chat_ownership
from app.crud.crud_message import add_message
from app.exceptions import AuthorizationError, ExtensionsError
from app.utils.parsers import parse_docx_bytes, parse_pdf_bytes

def add_user_message(
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

    Returns:
        MessageResponse with the bot's reply.
    """
    # Check if user owns chat 
    if not chat_ownership(db, chat_id, user_id):
        raise AuthorizationError("Not Authorized")

    # Save user's text message
    user_message = add_message(db, chat_id, "user", msg_in.text)

    #try:
        # get bot's response with user_message
    #    bot_response = call_bot(db, chat_id, user_message.text)
    #except BotException as e:
    #    raise BotException(f"Bot call failed: {str(e)}") 

    # Save bot's reposne 
    #bot_message = add_message(db, chat_id, "bot", bot_response)

    # Placeholder bot response until LLM integration is done
    bot_message = add_message(db, chat_id, "bot", "Bot has replied to your text.")

    message_response = MessageResponse(sender="bot", text=bot_message.text)

    return message_response

def add_upload_message(
    db: Session,
    chat_id: int,
    user_id: int,
    file: UploadFile,
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
    
    return add_user_message(db, chat_id, user_id, MessageRequest(text=parsed_text))