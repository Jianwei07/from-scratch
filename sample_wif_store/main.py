from fastapi import FastAPI, HTTPException
from models import ChatRequest, ChatResponse, ConversationHistory

from chat import ChatModel, ChatService, ConversationStore

app = FastAPI(title="Children's Chatbot")
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
