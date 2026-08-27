import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from models.schema import COLLECTION_INDEXES

load_dotenv()
logger = logging.getLogger(__name__)

class MongoService:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB_NAME", "apix_db")
        self.client = None
        self.db = None

    def connect(self):
        """Establish connection and create collection indexes."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            self._ensure_indexes()
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.warning(f"MongoDB connection failed (running in offline/mock mode if DB is local): {e}")

    def _ensure_indexes(self):
        """Initialize collection indexes defined in schema."""
        for coll_name, index_defs in COLLECTION_INDEXES.items():
            collection = self.db[coll_name]
            for index_keys in index_defs:
                collection.create_index(index_keys)

    def insert_raw_fares(self, fares: list):
        if self.db is not None and fares:
            return self.db["raw_fares"].insert_many(fares)

    def insert_cleaned_fares(self, fares: list):
        if self.db is not None and fares:
            return self.db["cleaned_fares"].insert_many(fares)

    def get_collection(self, name: str):
        if self.db is not None:
            return self.db[name]
        return None

mongo_db = MongoService()