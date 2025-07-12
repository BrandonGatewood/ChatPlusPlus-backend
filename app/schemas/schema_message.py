from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict


class MessageRequest(BaseModel):
    """
    Schema for incoming user message requests.
    """
    text: str
    files: Optional[List[UploadFile]] = None


class EditMessageRequest(BaseModel):
    """
    Schema for incoming user edit message requests.
    """
    text: str


class MessageResponse(BaseModel):
    """
    Schema representing a single message in a chat, used when displaying all messages 
    within a chat.
    """
    id: UUID
    sender: str
    text: str
    model_config = ConfigDict(from_attributes=True)
