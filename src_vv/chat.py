import asyncio
import re

from model import ChatRequest, ChatResponse

BLOCKED = {"weapon", "suicide", "die"}
SAFE_WORD = "Can't help u"


class ChatModel:
    async def generate(self, request: ChatRequest) -> str:
        await asyncio.sleep(0.1)
        return f"Chat: {request.message}"


def is_safe(text: str) -> bool:
    words = re.sub(r"[^a-z]", "", text.casefold())
    return not any(term in words for term in BLOCKED)

class ChatService:
    def __init__(self, model: ChatModel) -> None:
        self.model = model

    async def respond(self, request: ChatRequest) -> ChatResponse:
        if not is_safe(request.message):
            return ChatResponse(response=SAFE_WORD, blocked=True)
        reply = await self.model.generate(request)

        if not is_safe(reply):
            return ChatResponse(response=SAFE_WORD, blocked=True)

        return ChatResponse(response=reply)
