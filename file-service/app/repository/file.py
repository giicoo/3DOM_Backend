from typing import List
from bson import ObjectId
from fastapi import Depends
from app.core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.file import Chunk
from app.schemas.file import ChunkDocument
class FileRepository: 
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_chunks(self, chunks: List[Chunk]) -> List[str]:
        ids = await ChunkDocument.insert_many([ChunkDocument(id=chunk.id,
                                                 chat_id=chunk.chat_id,
                                                 filename=chunk.filename,
                                                 text=chunk.text,
                                                 chunk_index=chunk.chunk_index,
                                                 created_at=chunk.created_at) for chunk in chunks])
        return [str(i) for i in ids.inserted_ids]
    
    async def get_chunk_by_id(self, id: str) -> Chunk:
        chunkDB = await ChunkDocument.find_one(ChunkDocument.id==ObjectId(id))
        return Chunk(id=chunkDB.id,
                    filename=chunkDB.filename,
                    chunk_index=chunkDB.chunk_index,
                    text=chunkDB.text,
                    created_at=chunkDB.created_at)

def get_file_repo(db: AsyncIOMotorDatabase = Depends(get_db)):
    return FileRepository(db)