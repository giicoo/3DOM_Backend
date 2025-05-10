from typing import List
from bson import ObjectId
from fastapi import Depends
from app.schemas.chat import ChatDocument
from app.domain.chat import Chat
from app.core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


class ChatRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
        
    async def create_chat(self, chat: Chat) -> str:
        try:
            chatDB = ChatDocument(title=chat.title,
                                  telegram_id=chat.telegram_id,
                                  model=chat.model,
                                  created_at=chat.created_at)
            await chatDB.insert() 
            return str(chatDB.id)
        except Exception as e:
            raise Exception(f"chat repo: create chat: {e}")

    async def get_chat(self, chat_id: str) -> Chat:
        try:
            chatDB = await ChatDocument.get(ObjectId(chat_id))
            return Chat(id=str(chatDB.id),
                        telegram_id=chatDB.telegram_id,
                        title=chatDB.title,
                        model=chatDB.model,
                        token=chatDB.token,
                        created_at=chatDB.created_at)
        except Exception as e:
            raise Exception(f"chat repo: get chat: {e}")
    
    async def save_token(self, chat_id: str, token: str):
        try:
            chatDB = await ChatDocument.get(ObjectId(chat_id))
            chatDB.token = token
            await chatDB.save()
        except Exception as e:
            raise Exception(f"chat repo: save token: {e}")
    
    async def get_token(self, token: str):
        try:
            chatDB = await ChatDocument.find_one(ChatDocument.token==token)
            return Chat(id=str(chatDB.id),
                        telegram_id=chatDB.telegram_id,
                        title=chatDB.title,
                        model=chatDB.model,
                        token=chatDB.token,
                        created_at=chatDB.created_at)
        except Exception as e:
            raise Exception(f"chat repo: get token: {e}")

    async def get_chats_by_telegram_id(self, telegram_id: int) -> List[Chat]:
        try: 
            chatsDB = await ChatDocument.find(ChatDocument.telegram_id == telegram_id).to_list()
            chats = [Chat(id=str(chatDB.id),
                        telegram_id=chatDB.telegram_id,
                        title=chatDB.title,
                        model=chatDB.model,
                        token=chatDB.token,
                        created_at=chatDB.created_at) for chatDB in chatsDB]
            return chats
        except Exception as e:
            raise Exception(f"chat repo: get chat by tg id: {e}")

    async def delete_chat(self, chat_id: str):
        try:
            chat = await ChatDocument.get(ObjectId(chat_id))
            if chat:
                await chat.delete()
        except Exception as e:
            raise Exception(f"chat repo: delete chat: {e}")

def get_chat_repo(db: AsyncIOMotorDatabase = Depends(get_db)):
    return ChatRepository(db)