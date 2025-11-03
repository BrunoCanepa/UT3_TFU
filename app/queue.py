import os
from rq import Queue
from redis import Redis

_redis = None

def _get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))
    return _redis

def get_queue(name: str = "default") -> Queue:
    return Queue(name, connection=_get_redis())