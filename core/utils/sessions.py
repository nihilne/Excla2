import datetime
import secrets
from typing import Optional, Any

from fastapi import Request
from fastapi.responses import Response
from cachetools import TTLCache

_cache: TTLCache = TTLCache(maxsize=1024, ttl=3600)


class Session:
    def __init__(self, session_id: Optional[str] = None, is_new: bool = True):
        self.session_id = session_id
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
        _cache[session_id] = data
        return session_id

    @staticmethod
    async def fetch(session_id: str):
        return _cache.get(session_id)

    async def get(self, key: str) -> str | None:
        doc = _cache.get(self.session_id)
        if not doc:
            return None
        return doc["data"].get(key)

    async def set(self, key: str, value: Any) -> None:
        doc = _cache.get(self.session_id)
        if doc:
            doc["data"][key] = value
            _cache[self.session_id] = doc

    async def delete(self, key: str):
        doc = _cache.get(self.session_id)
        if doc:
            doc["data"].pop(key, None)
            _cache[self.session_id] = doc

    async def destroy(self) -> None:
        _cache.pop(self.session_id, None)

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
