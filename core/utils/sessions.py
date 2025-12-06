import datetime
import secrets
from typing import Optional, Any

from fastapi import Request
from fastapi.responses import Response

import core.utils.mongo as mongo


class Session:
    def __init__(self, session_id: Optional[str] = None, is_new: bool = True):
        self.session_id = session_id
        self.query = {"_id": self.session_id}
        self.is_new = is_new

    @classmethod
    async def load(cls, session_id: Optional[str] = None):
        if session_id:
            fetch_session = await cls.fetch(session_id)
            if fetch_session:
                return cls(fetch_session["_id"], False)

        new_id = await cls.new()
        return cls(new_id)

    @staticmethod
    async def new() -> str:
        session_id = secrets.token_urlsafe(32)
        data = {
            "_id": session_id,
            "createdAt": datetime.datetime.now(),
            "data": {},
        }
        await mongo.db.sessions.insert_one(data)
        return session_id

    @staticmethod
    async def fetch(session_id: str):
        return await mongo.db.sessions.find_one({"_id": session_id})

    # DATA MANIPULATION

    async def get(self, key: str) -> str | None:
        doc = await mongo.db.sessions.find_one({"_id": self.session_id})
        if not doc:
            return None
        return doc["data"][key]

    async def set(self, key: str, value: Any) -> None:
        await mongo.db.sessions.update_one(
            self.query,
            {"$set": {f"data.{key}": value}},
        )

    async def delete(self, key: str):
        await mongo.db.sessions.update_one(
            self.query,
            {"$unset": {f"data.{key}": ""}},
        )

    async def destroy(self) -> None:
        await mongo.db.sessions.delete_one(self.query)

    # COOKIE MANIPULATION

    def set_cookie(self, response: Response) -> None:
        if self.session_id:
            return response.set_cookie(
                key="SID",
                value=self.session_id,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=3600,
                path="/",
            )

    @staticmethod
    def get_cookie(request: Request) -> Optional[str]:
        return request.cookies.get("SID")

    @staticmethod
    def clear_cookie(response: Response) -> None:
        return response.delete_cookie("SID")
