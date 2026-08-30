"""
MongoDB Asynchronous Client Manager for FastAPI lifespan.
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("APIMongo")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "apix_db")


class MongoDBManager:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_db(cls):
        try:
            cls.client = AsyncIOMotorClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10
            )
            cls.db = cls.client[DATABASE_NAME]
            await cls.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB via Motor.")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB running in offline fallback mode: {e}")

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            logger.info("🔒 MongoDB connection closed.")


mongo_db = MongoDBManager()