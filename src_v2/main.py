from fastapi import FastAPI

from chat import ChatModel, ChatService
from model import ChatRequest, ChatResponse

app = FastAPI()

chat_svc = ChatService(ChatModel())

@app.post("/chat", response_model=ChatResponse)
async def chat(request:ChatRequest) -> ChatResponse:
    return await chat_svc.respond(request)