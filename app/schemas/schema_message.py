from pydantic import BaseModel

class MessageRequest(BaseModel):
    """
    Schema for incoming user message requests.
    """
    text: str

class MessageResponse(BaseModel):
    """
    Schema for outgoing bot responses.
    """
    text: str