from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

NonBlank = Annotated[
    str,
    StringConstraints(strip_whitespace=True,min_length=1,max_length=200)
]

class ChatRequest(BaseModel):
    message: NonBlank
    age: int = Field(ge=8,le=15)

class ChatResponse(BaseModel):
    response: NonBlank
    blocked: bool = False

class ChatMessage(BaseModel):
    role: Literal["user", "chatbot"]
    content: str

class ConvoHistory(BaseModel):
    conv_id: str
    history: list[ChatMessage]