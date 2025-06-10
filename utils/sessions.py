import secrets
import mongo

from typing import Optional


class Session:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id

    @classmethod
    async def load(cls, session_id: Optional[str] = None):
        if session_id:
            fetch_session = await cls.fetch(session_id)
            if fetch_session:
                return cls(fetch_session["_id"])

        new_id = await cls.new()
        return cls(new_id)

    @staticmethod
    async def new() -> str:
        session_id = secrets.token_urlsafe(32)
        data = {
            "_id": session_id,
            "data": {},
        }
        await mongo.db.sessions.insert_one(data)
        return session_id

    @staticmethod
    async def fetch(session_id: str):
        query = {"_id": session_id}
        return await mongo.db.sessions.find_one(query)

    async def get(self, key: str) -> None:
        query = {"_id": self.session_id}
        await mongo.db.sessions.find_one()

    async def set(self, key: str): ...

    async def destroy(self): ...
