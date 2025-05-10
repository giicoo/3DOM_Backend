from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sse_starlette import EventSourceResponse
from app.services.ollama import OllamaService, get_ollama_service
from app.schemas.ollama import OllamaChatIn
from app.domain.ollama import OllamaChat

OllamaRouter = APIRouter(
    tags=["ollama"]
)

@OllamaRouter.get("/generate-chat-title")
async def create_message(query: str, ollamaService: OllamaService = Depends(get_ollama_service)):
    title = await ollamaService.generate_chat_title(query=query)
    return JSONResponse({"title":title})

@OllamaRouter.post("/embedding")
async def create_embedding(input: List[str], ollamaService: OllamaService = Depends(get_ollama_service)):
    embedding = await ollamaService.embedding(input)
    return JSONResponse({"embedding": embedding.model_dump_json()})

@OllamaRouter.post("/stream")
async def stream(chat: OllamaChatIn, ollamaService: OllamaService = Depends(get_ollama_service)):
    return EventSourceResponse(ollamaService.stream(chat=OllamaChat(model=chat.model,
                                                                    msgs=chat.msgs,
                                                                    context=chat.context)))