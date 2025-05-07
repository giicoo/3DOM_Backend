import uuid
from bson import ObjectId
from fastapi import Depends
from app.core.database import get_chrome_db, get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from chromadbx import DocumentSHA256Generator
from chromadb.api.models.AsyncCollection import AsyncCollection




class ChromeRepository: 
    def __init__(self, db: AsyncCollection):
        self.db = db

    async def save(self, text: str):
        await self.db.add(ids=[DocumentSHA256Generator(documents=text)],
                    documents=[text])
        
def get_chrome_repo(db: AsyncCollection = Depends(get_chrome_db)):
    return ChromeRepository(db)