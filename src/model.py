from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]

class ChatRequest(BaseModel):
    message: NonBlank
    age: int = Field(ge=8, le=12)

class ChatResponse(BaseModel):
    response: NonBlank
    blocked: bool = False