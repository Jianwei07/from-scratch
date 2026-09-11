from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

NonBlankText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
]


class ChatRequest(BaseModel):
    message: NonBlankText
    age: int = Field(ge=8, le=12)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    blocked: bool = False


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: list[ChatMessage]
