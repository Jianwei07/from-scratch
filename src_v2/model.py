from typing import Annotated

from pydantic import BaseModel, StringConstraints

NonBlank = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)
]


class ChatRequest(BaseModel):
    message: NonBlank


class ChatResponse(BaseModel):
    response: NonBlank
    blocked: bool = False
