# app/db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

def get_mongo_client():
    if os.getenv("MODE") == "development":
        client = AsyncIOMotorClient(os.getenv("MONGO_URL_DEV"))
    else:
        client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    return client["basketballboard"]  # este es tu database

# 👉 colección lista para importar
plays_collection = get_mongo_client()["plays_data"]
