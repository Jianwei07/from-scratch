import re
from uuid import uuid4

from models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistory,
)

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
    async def generate(
        self,
        request: ChatRequest,
        history: list[ChatMessage],
    ) -> str:
        # A real external LLM/network call would be awaited at this seam.
        return f"Chat: {request.message}"


class ConversationStore:
    """In-memory conversation history for this single-worker demo."""

    def __init__(self) -> None:
        self._conversations: dict[str, list[ChatMessage]] = {}

    def open(self, conversation_id: str | None) -> str:
        conversation_id = conversation_id or uuid4().hex
        self._conversations.setdefault(conversation_id, [])
        return conversation_id

    def add(self, conversation_id: str, message: ChatMessage) -> None:
        self._conversations[conversation_id].append(message)

    def get(self, conversation_id: str) -> list[ChatMessage]:
        if conversation_id not in self._conversations:
            raise KeyError(conversation_id)

        return list(self._conversations[conversation_id])


class ChatService:
    def __init__(self, model: ChatModel, store: ConversationStore) -> None:
        self.model = model
        self.store = store

    async def respond(self, request: ChatRequest) -> ChatResponse:
        conversation_id = self.store.open(request.conversation_id)
        blocked = not is_safe(request.message)

        if blocked:
            reply = SAFE_REPLY
        else:
            history = self.store.get(conversation_id)
            reply = await self.model.generate(request, history)
            blocked = not is_safe(reply)
            if blocked:
                reply = SAFE_REPLY

        self.store.add(
            conversation_id,
            ChatMessage(role="user", content=request.message),
        )
        self.store.add(
            conversation_id,
            ChatMessage(role="assistant", content=reply),
        )

        return ChatResponse(
            conversation_id=conversation_id,
            response=reply,
            blocked=blocked,
        )

    def get_history(self, conversation_id: str) -> ConversationHistory:
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=self.store.get(conversation_id),
        )
