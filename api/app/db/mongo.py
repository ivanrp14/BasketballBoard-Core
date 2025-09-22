from motor.motor_asyncio import AsyncIOMotorClient
import os

def get_mongo_client():
    if os.getenv("MODE") == "development":
        client = AsyncIOMotorClient(os.getenv("MONGO_URL_DEV"))
    else:
        client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    return client.pizarra  # database name
