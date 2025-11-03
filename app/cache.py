import os, json
from redis import Redis

_redis = None

def get_redis() -> Redis:
    global _redis
    if _redis is None:
        url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        _redis = Redis.from_url(url, decode_responses=True)
    return _redis

def cache_get(key: str):
    return get_redis().get(key)

def cache_set(key: str, value, ttl_seconds: int = 60):
    payload = value if isinstance(value, str) else json.dumps(value)
    get_redis().setex(key, ttl_seconds, payload)

def cache_del(key: str):
    get_redis().delete(key)