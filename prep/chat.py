import re

from model import ChatRequest, ChatResponse

BLOCKED = frozenset({"suicide","weapon","die"})
BLOCKED_LEN = max(map(len,BLOCKED))
FALLBACK = "I can't help you with that"

class ChatModel: ## Mimic chat responses
    async def generate(self, request:ChatRequest) -> str:
        return f"Chat: {request.message}"

def is_safe(text:str) -> bool:
    words = re.findall(r"[a-z]+",text.casefold())
    return BLOCKED.isdisjoint(words)    

class ChatService:
    def __init__(self, model = ChatModel) -> None:
        self.model = model

    async def respond(self, request: ChatRequest) -> ChatResponse:
        if not is_safe(request.message):
            return self._blocked_words()
        
        reply = await self.model.generate(request)

        if not is_safe(reply):
            return self._blocked_words()
        
        return ChatResponse(response=reply)

    @staticmethod
    def _blocked_words() -> ChatResponse:
        return ChatResponse(response=FALLBACK,blocked=True)


