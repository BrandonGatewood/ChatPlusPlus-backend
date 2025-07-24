from typing import List
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.exceptions import ExtensionsError
from app.crud.crud_message import add_message
from app.utils.parsers import parse_pdf_bytes, parse_docx_bytes
from app.schemas.schema_message import MessageRequest, MessageResponse


"""
Shared service functions for message handling:
"""


def save_user_messages(
    db: Session,
    chat_id: UUID,
    msg_in: MessageRequest
) -> List[MessageResponse]:
    """
    Save user text and uploaded files as messages in the DB.

    Args:
        db: SQLAlchemy DB session.
        chat_id: The chat_id's unique ID.
        msg_in: MessageRequest object containing text and optional files.

    Returns:
        The list of MessageResponse instance containing the id, sender, and text.
    """
    message_responses = [] 
    message_response = add_message(db, chat_id, "user", msg_in.text)
    message_responses.append(message_response)

    if msg_in.files:
        for file in msg_in.files:
            parsed_text = parse_file(file)
            message_response = add_message(db, chat_id, "user", parsed_text)
            message_responses.append(message_response)
    
    return message_responses


def parse_file(
    file: UploadFile
) -> str:
    """
    Parse uploaded file content to extract text for supported formats.
    Raises error for unsupported or empty files.

    Args:
        file: UploadFile object representing the uploaded file.

    Raises:
        ExtensionsError: If file extension is not PDF or DOCX.
        ExtensionsError: If the file is empty or cannot be read.

    Returns:
        The string extracted content of the file.
    """
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ["pdf", "docx"]:
        raise ExtensionsError("Unsupported file type. Upload PDF or DOCX.")

    with file.file as f:
        file_bytes = f.read()

    if not file_bytes:
        raise ExtensionsError(f"File {file.filename} is empty or could not be read.")

    return parse_pdf_bytes(file_bytes) if file_ext == "pdf" else parse_docx_bytes(file_bytes)
