import asyncio
import re
from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel, Field, StringConstraints

app = FastAPI(title="Children's Chatbot")

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


BLOCKED_TERMS = frozenset({"kill", "suicide", "weapon", "weapons"})
MAX_BLOCKED_LENGTH = max(map(len, BLOCKED_TERMS))
SAFE_REPLY = "I can't help with that. Please ask a trusted adult."


def is_safe(text: str) -> bool:
    """Detect exact blocked terms, including terms split by spaces."""
    words = re.findall(r"[a-z]+", text.casefold())

    # ponytail: heuristic filter; use moderation when semantic safety is required.
    for start in range(len(words)):
        candidate = ""
        for word in words[start:]:
            candidate += word
            if len(candidate) > MAX_BLOCKED_LENGTH:
                break
            if candidate in BLOCKED_TERMS:
                return False

    return True


class ChatModel:
    async def generate(self, request: ChatRequest) -> str:
        # A real external LLM/network call would be awaited at this seam.
        return f"Chat: {request.message}"


class ChatService:
    def __init__(self, model: ChatModel) -> None:
        self.model = model

    async def respond(self, request: ChatRequest) -> ChatResponse:
        if not is_safe(request.message):
            return self._blocked_response()

        reply = await self.model.generate(request)
        if not is_safe(reply):
            return self._blocked_response()

        return ChatResponse(response=reply)

    @staticmethod
    def _blocked_response() -> ChatResponse:
        return ChatResponse(response=SAFE_REPLY, blocked=True)


chat_service = ChatService(ChatModel())


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await chat_service.respond(request)


async def _self_check() -> None:
    safe = await chat_service.respond(
        ChatRequest(message="Why is the sky blue?", age=9)
    )
    assert not safe.blocked
    assert is_safe("I learned a new skill")

    blocked = await chat_service.respond(
        ChatRequest(message="Tell me about a wea po n", age=9)
    )
    assert blocked.blocked


if __name__ == "__main__":
    asyncio.run(_self_check())
