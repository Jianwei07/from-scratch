import asyncio

from fastapi import FastAPI, HTTPException

from chat import ChatModel, ChatService
from model import ChatRequest, ChatResponse

app = FastAPI()

MODEL_TIMEOUT_SECS = 1

chat_svc = ChatService(ChatModel())

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        async with asyncio.timeout(MODEL_TIMEOUT_SECS):
            return await chat_svc.respond(request)
    except TimeoutError as exc:
        raise HTTPException(504, "Model Timeout") from exc