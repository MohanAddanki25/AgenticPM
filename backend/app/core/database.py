"""
MongoDB connection layer.

Uses Motor (async MongoDB driver) against a real MongoDB / MongoDB Atlas
instance when reachable. If USE_MOCK_DB_FALLBACK is enabled and the real
Mongo server cannot be reached (e.g. local demo without Docker/Atlas),
falls back transparently to `mongomock` so the whole system remains fully
runnable and demonstrable out of the box. This fallback is ONLY for local
developer convenience - production deployments must set a real MONGO_URI.
"""
import logging
import socket
import certifi
from app.core.config import settings

logger = logging.getLogger("database")

# Force IPv4 to avoid NAT64/IPv6 TLS handshake failures with MongoDB Atlas
_original_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(*args, **kwargs):
    results = _original_getaddrinfo(*args, **kwargs)
    ipv4 = [r for r in results if r[0] == socket.AF_INET]
    return ipv4 if ipv4 else results
socket.getaddrinfo = _ipv4_getaddrinfo


_client = None
_db = None
_using_mock = False


async def connect_to_mongo():
    global _client, _db, _using_mock
    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            tlsCAFile=certifi.where(),
        )
        # Use the async admin ping to verify connectivity
        await client.admin.command("ping")
        _client = client
        _db = client[settings.MONGO_DB_NAME]
        _using_mock = False
        logger.info("Connected to real MongoDB successfully")
    except Exception as exc:  # noqa: BLE001
        if not settings.USE_MOCK_DB_FALLBACK:
            raise
        logger.warning(
            "Could not connect to MongoDB (%s). Falling back to in-memory "
            "mongomock database for local demo purposes.",
            exc,
        )
        from mongomock_motor import AsyncMongoMockClient

        _client = AsyncMongoMockClient()
        _db = _client[settings.MONGO_DB_NAME]
        _using_mock = True


def get_db():
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return _db


def is_using_mock() -> bool:
    return _using_mock
