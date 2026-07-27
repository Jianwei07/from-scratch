import re

from model import ChatRequest, ChatResponse

BLOCKED_WORDS = {"suicide", "weapon"}
MAX_BK_LEN = max(map(len, BLOCKED_WORDS))
SAFE_REPLY = "I can't help you with that."


class ChatModel:
    async def generate(self, request: ChatRequest) -> str:
        return f"Chat: {request.message}"


def is_safe(text: str) -> bool:
    words = re.sub(r"[^a-z]", "", text.casefold())
    return not any(val in words for val in BLOCKED_WORDS)


class ChatService:
    def __init__(self, model: ChatModel) -> None:  # able to take OpenAImodel() as well
        self.model = model

    async def respond(self, request: ChatRequest) -> ChatResponse:
        if not is_safe(request.message):
            return ChatResponse(response=SAFE_REPLY, blocked=True)

        reply = await self.model.generate(request)

        if not is_safe(reply):
            return ChatResponse(response=SAFE_REPLY, blocked=True)

        return ChatResponse(response=reply)
