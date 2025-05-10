from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.environment import MONGO_URI
from app.core.log import Logger


async def connect_to_mongo():
    client = AsyncIOMotorClient(MONGO_URI)
    Logger.info("MongoDB connected")
    return client

async def close_mongo_connection(client: AsyncIOMotorClient):
    client.close()
    Logger.info("MongoDB connection closed")

def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.mongo_client["db"]

