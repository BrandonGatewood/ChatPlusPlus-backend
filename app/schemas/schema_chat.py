from pydantic import BaseModel

class ChatSummary(BaseModel):
    id: int
    title: str