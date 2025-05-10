from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId


class ChatScheme(BaseModel):
    id: Optional[PydanticObjectId] 
    telegram_id: int 
    title: str 
    model: str 
    token: str 
    created_at: datetime 


    class Config:
        json_encoders = {PydanticObjectId: str}


class ChatDocument(ChatScheme, Document):
    pass

class ChatIn(BaseModel):
    telegram_id: int
    model: str
    title: str

class ChatOut(BaseModel):
    id: Optional[PydanticObjectId]
    telegram_id: int
    model: str
    title: str
    created_at: datetime 


    class Config:
        json_encoders = {PydanticObjectId: str}