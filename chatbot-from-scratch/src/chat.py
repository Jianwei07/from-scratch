import re

from model import ChatRequest, ChatResponse

BLOCKED_TERMS = frozenset({"suicide", "weapon", "weapons"})
MAX_BLOCKED_LENGTH = max(map(len, BLOCKED_TERMS))
SAFE_REPLY = "I can't help with that. Please ask a trusted adult."


class ChatModel:
    async def generate(self, request: ChatRequest) -> str:
        return f"Chat: {request.message}"

# def is_safe(text:str) -> bool:
#     words = re.sub(r"[^a-z]", "",text.casefold())
#     return not any(term in words for term in BLOCKED)

def is_safe(text: str) -> bool:
    words = re.findall(r"[a-z]+", text.casefold())

    # ponytail: heuristic filter; use moderation for semantic safety.
    for start in range(len(words)):
        candidate = ""
        for word in words[start:]:
            candidate += word
            if len(candidate) > MAX_BLOCKED_LENGTH:
                break
            if candidate in BLOCKED_TERMS:
                return False

    return True


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
