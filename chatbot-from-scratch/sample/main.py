from fastapi import FastAPI
from models import ChatRequest, ChatResponse

from chat import ChatModel, ChatService

app = FastAPI(title="Children's Chatbot")
chat_service = ChatService(ChatModel())


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await chat_service.respond(request)
