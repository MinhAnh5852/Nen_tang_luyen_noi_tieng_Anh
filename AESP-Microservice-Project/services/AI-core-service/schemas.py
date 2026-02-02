from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    text: str
    topic: str

class ChatResponse(BaseModel):
    reply: str
    correction: Optional[str]
    accuracy: int