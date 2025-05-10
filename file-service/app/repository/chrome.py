from typing import List
import uuid
from bson import ObjectId
from fastapi import Depends
from app.core.database import get_chrome_db, get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from chromadb.api.models.AsyncCollection import AsyncCollection
from app.core.log import Logger
from app.core.error import APIError
from app.domain.file import Chunk


class ChromaRepository: 
    def __init__(self, db: AsyncCollection):
        self.db = db

    async def save(self, chunks: List[Chunk], embeddings):
        try:
            await self.db.add(ids=[c.id for c in chunks],
                            documents=[c.text for c in chunks],
                            embeddings=embeddings,
                            metadatas=[{"chat_id":c.chat_id} for c in chunks])
            
            
            
        except Exception as e:
            raise Exception(f"chroma repository: save: {e}")
    
    async def query(self, ids: List[str], n:int, embeddings) -> List[str]:
        try:
            results = await self.db.query(
                ids=ids,
                query_embeddings=embeddings,
                n_results=n,
                )
            return results["documents"][0]
        except Exception as e:
            raise Exception(f"chroma repository: query: {e}")
        
def get_chroma_repo(db: AsyncCollection = Depends(get_chrome_db)):
    return ChromaRepository(db)