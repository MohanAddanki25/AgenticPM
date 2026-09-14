"""
Redis client used for agent workflow state + caching.

Falls back to an in-process dict-backed stub if a real Redis server is not
reachable, so the demo remains runnable without infra. Production
deployments should always configure REDIS_URL to a real Redis instance
(e.g. Render Redis / Upstash).
"""
import json
import logging
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger("redis_client")


class _InMemoryRedisStub:
    """Minimal drop-in replacement implementing the subset of the redis-py
    async API this project uses, backed by a process-local dict."""

    def __init__(self):
        self._store: dict[str, str] = {}

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        self._store[key] = value
        return True

    async def get(self, key: str):
        return self._store.get(key)

    async def delete(self, key: str):
        self._store.pop(key, None)
        return True

    async def ping(self):
        return True


_redis = None


async def connect_to_redis():
    global _redis
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        await client.ping()
        _redis = client
        logger.info("Connected to real Redis at %s", settings.REDIS_URL)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not connect to Redis (%s). Using in-memory stub.", exc)
        _redis = _InMemoryRedisStub()


def get_redis():
    if _redis is None:
        raise RuntimeError("Redis not initialized. Call connect_to_redis() first.")
    return _redis


async def save_workflow_state(run_id: str, state: dict, ttl_seconds: int = 3600):
    r = get_redis()
    await r.set(f"agent_run:{run_id}", json.dumps(state), ex=ttl_seconds)


async def load_workflow_state(run_id: str) -> Optional[dict]:
    r = get_redis()
    raw = await r.get(f"agent_run:{run_id}")
    return json.loads(raw) if raw else None
