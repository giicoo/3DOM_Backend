from typing import List
from bson import ObjectId
from fastapi import Depends
from app.core.database import get_db
from app.core.log import Logger
from app.domain.message import Message
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.message import MessageDocument


class MessageRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        

    async def create_message(self, msg: Message) -> str:
        try:
            
            message = MessageDocument(chat_id=ObjectId(msg.chat_id),
                                    parent_id=None,
                                    res_ids=msg.res_ids,
                                    content=msg.content,
                                    role=msg.role,
                                    created_at=msg.created_at)
            if msg.parent_id:
                message.parent_id = msg.parent_id
            await message.save()
            
            return str(message.id)
        except Exception as e:
            raise Exception(f"message repo: create message: {e}")
    
    async def get_message(self, id: str) -> Message:
        try: 
            message = await MessageDocument.find_one(MessageDocument.id==ObjectId(id))
            if not message:
                return Message()
            
            return Message(id=message.id,
                        chat_id=message.chat_id,
                        parent_id=message.parent_id,
                        res_ids=message.res_ids,
                        role=message.role,
                        content=message.content,
                        created_at=message.created_at)
        except Exception as e:
            raise Exception(f"message repo: get message: {e}")
    
    async def get_messages(self, chat_id: str) -> List[Message]:
        try:
            messages = await MessageDocument.find_many(MessageDocument.chat_id==ObjectId(chat_id)).to_list()
            return [Message(id=msg.id,
                            chat_id=msg.chat_id,
                            parent_id=msg.parent_id,
                            res_ids=msg.res_ids,
                            role=msg.role,
                            content=msg.content,
                            created_at=msg.created_at) for msg in messages]
        except Exception as e:
            raise Exception(f"message repo: get all messages: {e}")

def get_msg_repo(db: AsyncIOMotorDatabase = Depends(get_db)):
    return MessageRepository(db)