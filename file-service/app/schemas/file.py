from datetime import datetime
from typing import List, Literal, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

class ChunkSchema(BaseModel):
    id: Optional[PydanticObjectId] 
    chat_id: Optional[PydanticObjectId]
    filename: str 
    chunk_index: int
    text: str 
    created_at: datetime 

    class Config:
        json_encoders = {PydanticObjectId: str}


class ChunkDocument(ChunkSchema, Document):
    pass

class Properties(BaseModel):
    chat_id: Optional[PydanticObjectId]

    class Config:
        json_encoders = {PydanticObjectId: str}

class ContextIn(BaseModel):
    ids: Optional[List[PydanticObjectId]]
    prompt: Optional[str]

    class Config:
        json_encoders = {PydanticObjectId: str}

class ContextOut(ContextIn):
    context: List[str]