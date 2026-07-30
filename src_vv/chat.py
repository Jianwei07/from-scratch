import asyncio
import re

from model import ChatRequest, ChatResponse

BLOCKED_WRDS = {"die","suicide","weapon"}
FALLBACK = "I can't help you with that, please consult an adult."

class ChatModel: ## Simulate Response
    async def generate(self, request: ChatRequest) -> str:
        await asyncio.sleep(0.1)
        return f"Chat: {request.message}"


def is_safe(text:str) -> bool:
    words = re.findall(r"[a-z]+", text.casefold())
    return BLOCKED_WRDS.isdisjoint(words)

class ChatService:
    def __init__(self, model:ChatModel) -> None:
        self.model = model

    async def respond(self, request:ChatRequest) -> ChatResponse:
        if not is_safe(request.message):
            return ChatResponse(response=FALLBACK,blocked = True)
        reply = await self.model.generate(request)

        if not is_safe(reply):
            return ChatResponse(response=FALLBACK,blocked = True)

        return ChatResponse(response=reply)