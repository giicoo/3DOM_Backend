from bson import ObjectId
from fastapi import Depends
from app.core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase



class FileRepository: 
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

def get_file_repo(db: AsyncIOMotorDatabase = Depends(get_db)):
    return FileRepository(db)