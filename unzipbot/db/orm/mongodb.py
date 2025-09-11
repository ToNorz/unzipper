from base import DatabaseInterface, TableInterface
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.cursor import AsyncCursor
from pymongo.asynchronous.database import AsyncDatabase


class MongoTable(TableInterface):
    def __init__(self, collection) -> None:
        self.collection: AsyncCollection = collection

    async def count(self, filter: dict | None = None) -> int:
        filter = filter or {}

        return await self.collection.count_documents(filter=filter)

    async def find_one(self, query: dict) -> dict | None:
        return await self.collection.find_one(filter=query)

    async def get_all(self) -> list:
        cursor: AsyncCursor = self.collection.find({})

        return [doc async for doc in cursor]

    async def insert(self, document: dict) -> None:
        await self.collection.insert_one(document=document)

    async def update(self, query: dict, update: dict) -> None:
        await self.collection.update_one(filter=query, update={"$set": update})

    async def delete(self, query: dict) -> None:
        await self.collection.delete_one(filter=query)

    async def delete_all(self) -> None:
        await self.collection.delete_many(filter={})


class MongoDBDatabase(DatabaseInterface):
    def __init__(self, connection_str: str, db_name: str) -> None:
        self.connection_str: str = connection_str
        self.db_name: str = db_name
        self.client = AsyncMongoClient(host=self.connection_str)
        self.db: AsyncDatabase = self.client[self.db_name]

    async def open(self) -> None:
        self.client = AsyncMongoClient(host=self.connection_str)
        self.db = self.client[self.db_name]

    async def close(self) -> None:
        await self.client.close()

    def table(self, table_name: str) -> TableInterface:
        return MongoTable(collection=self.db[table_name])

    async def get_all_database(self) -> dict:
        data: dict = {}
        collections: list[str] = await self.db.list_collection_names()

        for coll in collections:
            cursor: AsyncCursor = self.db[coll].find({})
            data[coll] = [doc async for doc in cursor]

        return data
