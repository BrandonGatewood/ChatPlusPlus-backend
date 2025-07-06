from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.exceptions import ExtensionsError
from app.crud.crud_message import add_message
from app.crud.crud_chat import get_messages_for_chat
from app.utils.parsers import parse_pdf_bytes, parse_docx_bytes
from app.schemas.schema_message import MessageRequest, MessageResponse

"""
Shared service functions for message handling:
"""

def save_user_messages(db: Session, chat_id: UUID, msg_in: MessageRequest) -> None:
    """
    Save user text and uploaded files as messages in the DB.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat_id's unique ID.
        msg_in: MessageRequest object containing text and optional files.

    Returns:
        None
    """
    add_message(db, chat_id, "user", msg_in.text)
    if msg_in.files:
        for file in msg_in.files:
            parsed_text = parse_file(file)
            add_message(db, chat_id, "user", parsed_text)

def build_prompt(db: Session, chat_id: UUID) -> str:
    """
    Concatenate all messages in a chat into a single prompt string.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat_id's unique ID.

    Returns:
        The combined prompt string from chat messages.
    """
    messages = get_messages_for_chat(db, chat_id)
    return "\n\n".join(msg.text for msg in messages)

def parse_file(file: UploadFile) -> str:
    """
    Parse uploaded file content to extract text for supported formats.
    Raises error for unsupported or empty files.

    Args:
        file: UploadFile object representing the uploaded file.

    Raises:
        ExtensionsError: If file extension is not PDF or DOCX.
        ExtensionsError: If the file is empty or cannot be read.

    Returns:
        Extracted text content of the file.
    """
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ["pdf", "docx"]:
        raise ExtensionsError("Unsupported file type. Upload PDF or DOCX.")

    with file.file as f:
        file_bytes = f.read()

    if not file_bytes:
        raise ExtensionsError(f"File {file.filename} is empty or could not be read.")

    return parse_pdf_bytes(file_bytes) if file_ext == "pdf" else parse_docx_bytes(file_bytes)

def call_bot(prompt: str) -> MessageResponse:
    """
    Stub function to simulate bot response generation.

    Args:
        prompt: The prompt string to send to the bot.

    Returns:
        MessageResponse containing the bot's text reply.
    """
    return MessageResponse(text="Bot responded.")