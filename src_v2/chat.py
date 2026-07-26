import re

from model import ChatRequest, ChatResponse

BLOCKED_WORDS = {"suicide","weapon"}
SAFE_REPLY = "I can't help you with this, please consult a trustable adult."

class ChatModel:
    async def generate(self, request:ChatRequest) -> str:
        return f"Chat {request.message}"


def is_safe(text:str) -> bool:
    words = set(re.findall(r"[a-z]+",text.casefold()))
    return words.isdisjoint(BLOCKED_WORDS)

class ChatService:
    def __init__(self, model=ChatModel) -> None:
        self.model = model
        
    async def respond(self, request:ChatRequest) -> ChatResponse:
        if not is_safe(request.message):
            return ChatResponse(response=SAFE_REPLY,blocked=True)

        reply = await self.model.generate(request)

        if not is_safe(reply):
            return ChatResponse(response=SAFE_REPLY,blocked=True)
        return ChatResponse(response=reply)

