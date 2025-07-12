from typing import List
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.schema_message import MessageResponse


class ChatTitle(BaseModel):
    """
    Schema for a summarized chat object, used for displaying chat titles in chat lists.
    """
    id: UUID 
    title: str


class ChatResponse(BaseModel):
    """
    Schema for a detailed chat response, including chat metadata and a list of messages.
    """
    id: UUID
    title: str
    messages: List[MessageResponse]
    model_config = ConfigDict(from_attributes=True)
