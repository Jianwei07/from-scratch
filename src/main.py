from fastapi import FastAPI

from chat import ChatModel, ChatService
from model import ChatRequest, ChatResponse

app = FastAPI()
chat_model = ChatService(ChatModel())

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await chat_model.respond(request)