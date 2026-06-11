from pydantic import BaseModel
from typing import Optional


class EmailToSend(BaseModel):
    to_name: str = ""
    to_email: str
    subject: str = ""
    body: str = ""


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatFullRequest(BaseModel):
    messages: list[ChatMessage]
    session_id: Optional[str] = None


class ContactCreate(BaseModel):
    name: str
    email: str
    notes: str = ""
