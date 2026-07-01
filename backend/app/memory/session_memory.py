"""In-memory session store with optional Redis backend."""

from typing import Any, Dict, Optional

from backend.app.config import get_settings


class MemoryStore:
    """Simple in-memory key-value store for session data."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        return key in self._store

    def clear(self) -> None:
        self._store.clear()


class SessionMemory:
    """Session memory manager with optional Redis support."""

    def __init__(self) -> None:
        self._memory = MemoryStore()
        self._redis_client = None
        settings = get_settings()
        if settings.use_redis:
            try:
                import redis
                self._redis_client = redis.from_url(settings.redis_url)
            except Exception:
                self._redis_client = None

    def store_session(self, thread_id: str, data: Dict[str, Any]) -> None:
        self._memory.set(thread_id, data)
        if self._redis_client:
            import json
            self._redis_client.setex(thread_id, 3600, json.dumps(data, default=str))

    def get_session(self, thread_id: str) -> Optional[Dict[str, Any]]:
        cached = self._memory.get(thread_id)
        if cached:
            return cached
        if self._redis_client:
            import json
            data = self._redis_client.get(thread_id)
            if data:
                return json.loads(data)
        return None

    def delete_session(self, thread_id: str) -> None:
        self._memory.delete(thread_id)
        if self._redis_client:
            self._redis_client.delete(thread_id)


# Singleton instance
session_memory = SessionMemory()
