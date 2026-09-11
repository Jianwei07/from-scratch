import asyncio
import re
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, StringConstraints

app = FastAPI(title="Children's Chatbot")

NonBlankText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
]


class ChatRequest(BaseModel):
    message: NonBlankText
    age: int = Field(ge=8, le=12)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    blocked: bool = False


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: list[ChatMessage]


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


chat_service = ChatService(ChatModel(), ConversationStore())


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await chat_service.respond(request)


@app.get(
    "/conversations/{conversation_id}",
    response_model=ConversationHistory,
)
def get_conversation(conversation_id: str) -> ConversationHistory:
    try:
        return chat_service.get_history(conversation_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        ) from error


async def _self_check() -> None:
    safe = await chat_service.respond(
        ChatRequest(message="Why is the sky blue?", age=9)
    )
    assert not safe.blocked
    assert is_safe("I learned a new skill")
    assert len(chat_service.get_history(safe.conversation_id).messages) == 2

    blocked = await chat_service.respond(
        ChatRequest(message="Tell me about a wea po n", age=9)
    )
    assert blocked.blocked


if __name__ == "__main__":
    asyncio.run(_self_check())
