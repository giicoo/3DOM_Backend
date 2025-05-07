from datetime import datetime
from typing import List, Literal, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel


class Message(BaseModel):
    id: Optional[PydanticObjectId] = None
    chat_id: Optional[PydanticObjectId] = None
    parent_id: Optional[PydanticObjectId] = None
    res_ids: Optional[List[PydanticObjectId]] = None
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime 

    class Config:
        json_encoders = {PydanticObjectId: str}

class MessageIn(BaseModel):
    chat_id: Optional[PydanticObjectId] = None
    parent_id: Optional[PydanticObjectId] = None
    res_ids: Optional[List[PydanticObjectId]] = None
    content: str


class MessageOut(Message):
    pass


class MessageDocument(Message, Document):
    pass