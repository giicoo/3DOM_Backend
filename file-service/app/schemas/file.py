from datetime import datetime
from typing import List, Literal, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

class Metadata(BaseModel):
    source: str = None
    chunk_index: int = 0 
    page_number: int = 0
    created_at: datetime 

class File(BaseModel):
    id: Optional[PydanticObjectId] = None
    text: str
    metadata: Metadata
    
    class Config:
        json_encoders = {PydanticObjectId: str}


class FileDocument(File, Document):
    pass