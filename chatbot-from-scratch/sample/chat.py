import re

from models import ChatRequest, ChatResponse

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
