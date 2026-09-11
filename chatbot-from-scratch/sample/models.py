from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonBlankText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
]


class ChatRequest(BaseModel):
    message: NonBlankText
    age: int = Field(ge=8, le=12)


class ChatResponse(BaseModel):
    response: str
    blocked: bool = False
