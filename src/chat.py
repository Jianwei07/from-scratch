import re

from model import ChatRequest, ChatResponse

BLOCKED_WORDS = frozenset({"suicide", "weapon"})
FALLBACK = "I can't help you with that"

class ChatModel:
    async def generate(self, request:ChatRequest) -> str:
        return f"Chat {request.message}"


def is_safe(text:str) -> bool:
    words = set(re.findall(r"[a-z]+", text.casefold()))
    return words.isdisjoint(BLOCKED_WORDS)
    

class ChatService:
    def __init__(self, model:ChatModel) -> None:
        self.model = model

    async def respond(self, request:ChatRequest) -> ChatResponse:

        if not is_safe(request.message):
            return self._blocked_words()

        reply = await self.model.generate(request)
        if not is_safe(reply):
            return self._blocked_words()
        
        return ChatResponse(response=reply)

    @staticmethod
    def _blocked_words() -> ChatResponse:
        return ChatResponse(response=FALLBACK,blocked=True)