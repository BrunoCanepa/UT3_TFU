import os
from rq import Worker, Queue
from redis import Redis
from . import models
from .database import engine

if __name__ == "__main__":
    if os.getenv("RUN_DB_INIT", "false").lower() == "true":
        models.Base.metadata.create_all(bind=engine)

    url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    redis = Redis.from_url(url)
    q = Queue("default", connection=redis)
    Worker([q], connection=redis).work()