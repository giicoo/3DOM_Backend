import logging
from bson import ObjectId
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from app.core.log import Logger
from app.domain.chat import Chat
from app.repository.chat import ChatRepository
from app.schemas.chat import ChatIn, ChatOut
from app.services.chat import ChatService, get_chat_service

ChatRouter = APIRouter(
    tags=["chats"]
)

@ChatRouter.post("/create")
async def create_chat(chat: ChatIn, chatService: ChatService = Depends(get_chat_service)):
    
    chat_id = await chatService.create_chat(Chat(telegram_id=chat.telegram_id, 
                                                 model=chat.model, 
                                                 title=chat.title))
  
    return JSONResponse({"chat_id":chat_id}, 200)

@ChatRouter.post("/create-auto")
async def create_chat_auto(chat: ChatIn, query: str, chatService: ChatService = Depends(get_chat_service)):
    chat_id = await chatService.create_chat_auto(Chat(telegram_id=chat.telegram_id, 
                                                          model=chat.model), query)
    return JSONResponse({"chat_id":chat_id}, 200)

@ChatRouter.get("/get/{chat_id}", response_model=ChatOut)
async def get_chat(chat_id: str, chatService: ChatService = Depends(get_chat_service)):
    chat = await chatService.get_chat(chat_id)
    response = ChatOut(id=ObjectId(chat.id), 
                    telegram_id=chat.telegram_id, 
                    model=chat.model, 
                    title=chat.title,
                    token=chat.token,
                    created_at=chat.created_at)
    return response

@ChatRouter.get("/get-all/{telegram_id}", response_model=List[ChatOut])
async def get_chats(telegram_id: int, chatService: ChatService = Depends(get_chat_service)):
    chats = await chatService.get_chats_by_telegram_id(telegram_id)
    response: List[ChatOut] = []
    for chat in chats:
        response.append(ChatOut(id=ObjectId(chat.id), 
                                telegram_id=chat.telegram_id, 
                                model=chat.model, 
                                title=chat.title,
                                created_at=chat.created_at))
        
    return response

@ChatRouter.delete("/delete")
async def delete_chat(chat_id:str=None, chatService: ChatService = Depends(get_chat_service)):
    await chatService.delete_chat(chat_id)

@ChatRouter.post("/public")
async def public_chat(chat_id:str=None, chatService: ChatService = Depends(get_chat_service)):
    response = await chatService.create_public(chat_id)
    return JSONResponse({"token": response})

@ChatRouter.get("/public/{token}")
async def public_chat(token:str, chatService: ChatService = Depends(get_chat_service)):
    response = await chatService.get_public(token)
    return JSONResponse(response)