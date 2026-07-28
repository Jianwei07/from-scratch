import re

from model import ChatRequest, ChatResponse

BLOCKED = frozenset({"suicide","weapon"})
FALLBACK = "I can't help you with that, please consult an adult"

def is_safe(text:str) -> bool:
    words = re.sub(r"[^a-z]", "",text.casefold())
    return not any(term in words for term in BLOCKED)

class ChatModel: ## Mimic responses from LLM
    async def generate(self, request:ChatRequest) -> str:
        return f"Chat: {request.message}"

class ChatService:
    def __init__(self, model:ChatModel) -> None:
        self.model = model

    async def respond(self, request:ChatRequest) -> ChatResponse:
        if not is_safe(request.message):
            return ChatResponse(response=FALLBACK,blocked=True)
            
        reply = await self.model.generate(request)

        if not is_safe(reply):
            return ChatResponse(response=FALLBACK,blocked=True)
        
        return ChatResponse(response=reply)