import random
import string
from typing import List

from fastapi import Depends
import httpx
from app.core.environment import OLLAMA_URI
from app.core.log import Logger
from app.domain.chat import Chat
from app.repository.chat import ChatRepository, get_chat_repo
from app.schemas.chat import ChatDocument


class ChatService:
    def __init__(self, repository: ChatRepository):
        self.repo = repository

    async def create_chat_auto(self, chat: Chat, query: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=None) as client:

                title = await client.get(
                    "http://ollama-service:8000/generate-chat-title",
                    params={"query":query}
                )

                title = title.json()["title"]
            chat.title = title
            chatDB = ChatDocument(telegram_id=chat.telegram_id,model=chat.model,title=chat.title)
            resultDB = await self.repo.create_chat(chatDB)
            return str(resultDB.id)
        
        except Exception as e:
            raise Exception(f"chat service: create auto: {e}")
    
    async def create_public(self, chat_id: str):
        try:
            characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
            token = ''.join(random.choices(characters, k=24))
            await self.repo.save_token(chat_id=chat_id, token=token)
        
        except Exception as e:
            raise Exception(f"chat service: create auto: {e}")
        
    async def get_public(self, token: str):
        try:
            chat = await self.repo.get_token(token)
            async with httpx.AsyncClient(timeout=None) as client:

                response = await client.get(
                    "http://message-service:8000/messages",
                    params={"chat_id":chat.id}
                )

                response = response.json()
        except Exception as e:
            raise Exception(f"chat service: get public: {e}")
    
    async def create_chat(self, chat: Chat) -> str:
        try:
            chatDB = ChatDocument(telegram_id=chat.telegram_id,model=chat.model,title=chat.title)
            resultDB = await self.repo.create_chat(chatDB)
            return str(resultDB.id)

        except Exception as e:
            raise Exception(f"chat service: create: {e}")
        
    

    async def get_chat(self, chat_id: str) -> Chat:
        try:
            chat = await self.repo.get_chat(chat_id)
            return Chat(id=chat.id,
                    telegram_id=chat.telegram_id, 
                    model=chat.model,
                    title=chat.title,
                    created_at=chat.created_at)
        except Exception as e:
            raise Exception(f"chat get service: {e}")
        
        


    async def get_chats_by_telegram_id(self, telegram_id: int) -> List[Chat]:
        try: 
            chats = await self.repo.get_chats_by_telegram_id(telegram_id)

            chatsResponse = [Chat(id=chat.id,
                              telegram_id=chat.telegram_id, 
                              model=chat.model,
                              title=chat.title,
                              created_at=chat.created_at) for chat in chats]
            return chatsResponse
        except Exception as e:
            raise Exception(f"chat service: get by tg id: {e}")
        
        
        
        
    async def delete_chat(self, chat_id:str):
        try:
            await self.repo.delete_chat(chat_id)
        except Exception as e:
            raise Exception(f"chat service: delete: {e}")


def get_chat_service(repoMongo: ChatRepository = Depends(get_chat_repo)):
    return ChatService(repoMongo)